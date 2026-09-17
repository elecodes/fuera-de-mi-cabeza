from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from app.llm.providers import get_llm_client
from app.models.idea import IdeaInput
from app.models.session import EditorialSession
from app.services.session_manager import SessionManager
from app.services.idea_explorer import IdeaExplorer
from app.services.content_planner import ContentPlanner
from app.services.draft_generator import DraftGenerator
from app.services.voice_editor import VoiceEditor
from app.services.voice_auditor import VoiceAuditor
from app.services.argument_griller import ArgumentGriller
from app.memory.editorial_memory import EditorialMemory

app = FastAPI(title="Fuera de mi cabeza — Personal Editorial Agent", version="0.3.0")

session_manager = SessionManager()
editorial_memory = EditorialMemory()


# DTOs para solicitudes de la API
class AnswersInput(BaseModel):
    answers: list[str]


class SelectArcInput(BaseModel):
    arc_id: str


class DraftRequestInput(BaseModel):
    format: Literal["note", "article"] = "article"
    chosen_title: str | None = None


class UpdateDraftInput(BaseModel):
    title: str | None = None
    content: str


class AuditInput(BaseModel):
    content: str | None = None


class RevisionInput(BaseModel):
    feedback: str


class PreferenceInput(BaseModel):
    category: str
    preference: str


import os
import subprocess
import asyncio
import httpx

async def check_omniroute_running(base_url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            await client.get(base_url.rstrip('/'))
            return True
    except (httpx.ConnectError, httpx.TimeoutException):
        return False
    except Exception:
        return True


# Endpoints de estado del sistema y OmniRoute
@app.get("/api/system/status")
async def get_system_status():
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:20128/v1")
    omniroute_running = False

    if provider in ("openai-compatible", "omniroute", "omnirouter"):
        omniroute_running = await check_omniroute_running(base_url)

    return {
        "provider": provider,
        "base_url": base_url,
        "omniroute_running": omniroute_running,
    }


import shutil

@app.post("/api/system/omniroute/start")
async def start_omniroute():
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:20128/v1")

    if await check_omniroute_running(base_url):
        return {"message": "OmniRoute ya se encuentra activo.", "running": True}

    try:
        cmd = ["omniroute"] if shutil.which("omniroute") else (["omnirouter"] if shutil.which("omnirouter") else ["npx", "-y", "omniroute"])
        subprocess.Popen(cmd, env=os.environ.copy(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for _ in range(10):
            await asyncio.sleep(1.0)
            if await check_omniroute_running(base_url):
                return {"message": "OmniRoute se ha iniciado correctamente.", "running": True}

        return {
            "message": f"Se envió la orden de inicio, pero OmniRoute no respondió a tiempo en {base_url}. Probá iniciarlo manualmente en la terminal con 'npx omniroute'.",
            "running": False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo iniciar OmniRoute automáticamente: {str(e)}")


@app.post("/api/ideas", response_model=EditorialSession)
async def create_idea(input_data: IdeaInput):
    session = session_manager.create_session(original_idea=input_data.idea)
    if input_data.raw_thoughts:
        session.raw_thoughts = input_data.raw_thoughts
        session_manager.save_session(session)
    return session


@app.post("/api/ideas/{session_id}/explore", response_model=EditorialSession)
async def explore_idea(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    try:
        llm = get_llm_client()
        explorer = IdeaExplorer(llm_client=llm)
        analysis = await explorer.analyze(session.original_idea)

        session.analysis = analysis
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servicio LLM: {str(e)}")


@app.post("/api/ideas/{session_id}/select-arc", response_model=EditorialSession)
async def select_narrative_arc(session_id: str, payload: SelectArcInput):
    session = session_manager.get_session(session_id)
    if not session or not session.analysis:
        raise HTTPException(status_code=400, detail="La sesión debe haber completado el análisis previamente")

    matching_arc = next((arc for arc in session.analysis.narrative_arcs if arc.id == payload.arc_id), None)
    if not matching_arc:
        raise HTTPException(status_code=404, detail=f"Arco narrativo {payload.arc_id} no encontrado")

    session.selected_arc = matching_arc
    session_manager.save_session(session)
    return session


@app.post("/api/ideas/{session_id}/answers", response_model=EditorialSession)
async def submit_answers(session_id: str, payload: AnswersInput):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    session.user_answers = payload.answers
    session_manager.save_session(session)
    return session


@app.post("/api/ideas/{session_id}/grill", response_model=EditorialSession)
async def trigger_grill_mode(session_id: str):
    session = session_manager.get_session(session_id)
    if not session or not session.selected_arc:
        raise HTTPException(status_code=400, detail="Debes seleccionar un arco narrativo antes de activar el modo Grill")

    try:
        client = get_llm_client()
        griller = ArgumentGriller(llm_client=client)
        questions = await griller.generate_grill_questions(
            idea=session.original_idea,
            arc_title=session.selected_arc.title,
            thought_sequence=session.selected_arc.thought_sequence,
        )
        session.grill_mode = True
        session.grill_questions = questions
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el modo Grill: {str(e)}")


@app.post("/api/ideas/{session_id}/grill/answers", response_model=EditorialSession)
async def submit_grill_answers(session_id: str, payload: AnswersInput):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    session.grill_answers = payload.answers
    session_manager.save_session(session)
    return session


@app.post("/api/ideas/{session_id}/plan", response_model=EditorialSession)
async def plan_content(session_id: str):
    session = session_manager.get_session(session_id)
    if not session or not session.analysis:
        raise HTTPException(status_code=400, detail="La sesión debe haber completado el análisis previamente")

    try:
        llm = get_llm_client()
        planner = ContentPlanner(llm_client=llm)
        plan = await planner.plan(
            original_idea=session.original_idea,
            analysis=session.analysis,
            user_answers=session.user_answers,
            selected_arc=session.selected_arc,
            grill_answers=session.grill_answers,
        )

        session.content_plan = plan
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servicio LLM: {str(e)}")


@app.post("/api/ideas/{session_id}/draft", response_model=EditorialSession)
async def generate_draft(session_id: str, payload: DraftRequestInput):
    session = session_manager.get_session(session_id)
    if not session or not session.content_plan:
        raise HTTPException(status_code=400, detail="Se requiere un plan de contenido aprobado antes de generar un borrador")

    try:
        llm = get_llm_client()
        generator = DraftGenerator(llm_client=llm)

        fmt = payload.format or session.content_plan.format

        if fmt == "note":
            draft = await generator.generate_note(
                original_idea=session.original_idea,
                content_plan=session.content_plan,
                user_answers=session.user_answers,
            )
        else:
            draft = await generator.generate_article(
                original_idea=session.original_idea,
                content_plan=session.content_plan,
                user_answers=session.user_answers,
                chosen_title=payload.chosen_title,
            )

        session.draft = draft
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servicio LLM: {str(e)}")


@app.post("/api/ideas/{session_id}/draft/update", response_model=EditorialSession)
async def update_draft(session_id: str, payload: UpdateDraftInput):
    session = session_manager.get_session(session_id)
    if not session or not session.draft:
        raise HTTPException(status_code=400, detail="No hay un borrador activo para actualizar")

    session.draft.content = payload.content
    if payload.title is not None:
        session.draft.title = payload.title
    session_manager.save_session(session)
    return session


@app.post("/api/ideas/{session_id}/audit", response_model=EditorialSession)
async def audit_draft(session_id: str, payload: AuditInput | None = None):
    session = session_manager.get_session(session_id)
    if not session or not session.draft:
        raise HTTPException(status_code=400, detail="No existe un borrador para auditar")

    text_to_audit = (payload.content if payload and payload.content else session.draft.content)

    try:
        llm = get_llm_client()
        auditor = VoiceAuditor(llm_client=llm)
        audit_report = await auditor.audit(text_to_audit)

        session.voice_audit = audit_report
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al auditar la voz editorial: {str(e)}")


@app.post("/api/ideas/{session_id}/revise", response_model=EditorialSession)
async def revise_draft(session_id: str, payload: RevisionInput):
    session = session_manager.get_session(session_id)
    if not session or not session.draft:
        raise HTTPException(status_code=400, detail="No hay un borrador existente para revisar")

    try:
        llm = get_llm_client()
        editor = VoiceEditor(llm_client=llm)

        revised_draft = await editor.revise(
            original_idea=session.original_idea,
            current_draft=session.draft,
            feedback_text=payload.feedback,
        )

        session.feedback.append(payload.feedback)
        session.revisions.append(revised_draft.content)
        session.draft = revised_draft
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servicio LLM: {str(e)}")


@app.post("/api/memory/preference")
async def add_memory_preference(payload: PreferenceInput):
    editorial_memory.add_preference(payload.category, payload.preference)
    return {"message": "Preferencia guardada correctamente en memoria editorial."}


@app.get("/api/sessions/{session_id}", response_model=EditorialSession)
async def get_session_details(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


FAVICON_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%232c2c2c'/><path d='M50 20 L75 50 L60 80 L50 72 L40 80 L25 50 Z' fill='%23d97706'/><circle cx='50' cy='50' r='4' fill='%232c2c2c'/><line x1='50' y1='54' x2='50' y2='72' stroke='%232c2c2c' stroke-width='3'/></svg>"""


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


# Web UI & Architecture Diagram
WEB_DIR = Path(__file__).resolve().parent / "web"
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs" / "architecture"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Fuera de mi cabeza — API lista</h1>")


@app.get("/architecture", response_class=HTMLResponse)
async def serve_architecture():
    arch_file = DOCS_DIR / "archify_architecture.html"
    if arch_file.exists():
        return HTMLResponse(content=arch_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Diagrama de Arquitectura no encontrado</h1>", status_code=440)


@app.get("/architecture/sequence", response_class=HTMLResponse)
async def serve_architecture_sequence():
    seq_file = DOCS_DIR / "archify_sequence_flow.html"
    if seq_file.exists():
        return HTMLResponse(content=seq_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Diagrama de Secuencia no encontrado</h1>", status_code=440)


