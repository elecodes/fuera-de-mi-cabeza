from typing import Literal
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import tempfile
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
from app.services.profile_generator import ProfileGenerator
from app.services.audio_transcriber import AudioTranscriber
from app.memory.editorial_memory import EditorialMemory

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fuera de mi cabeza — Personal Editorial Agent", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    feedback: str = "Integrar las notas y modificaciones realizadas directamente en el borrador"


class PreferenceInput(BaseModel):
    category: str
    preference: str


class ProfileExtractInput(BaseModel):
    samples: list[str]


class LearnPreferenceInput(BaseModel):
    user_correction: str



import os
import subprocess
import asyncio
import httpx

import socket
from urllib.parse import urlparse

import httpx

async def check_omniroute_running(base_url: str) -> bool:
    url = f"{base_url.rstrip('/')}/models"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(url)
            if resp.status_code < 500:
                return True
    except Exception:
        pass

    try:
        parsed = urlparse(base_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 20128
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except Exception:
        pass

    return False





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

def get_enhanced_path() -> str:
    user_home = Path.home()
    extra_paths = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        str(user_home / ".bun" / "bin"),
    ]
    nvm_node_dir = user_home / ".nvm" / "versions" / "node"
    if nvm_node_dir.exists():
        for version_dir in nvm_node_dir.glob("*"):
            bin_dir = version_dir / "bin"
            if bin_dir.exists():
                extra_paths.append(str(bin_dir))

    current_path = os.environ.get("PATH", "")
    return os.pathsep.join(extra_paths + [current_path])


@app.post("/api/system/omniroute/start")
async def start_omniroute():
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:20128/v1")

    if await check_omniroute_running(base_url):
        return {"message": "OmniRoute ya se encuentra activo.", "running": True}

    try:
        parsed = urlparse(base_url)
        port = parsed.port or 20128
        # Intentar liberar puerto ocupado por procesos obsoletos
        try:
            subprocess.run("pkill -f omniroute || true", shell=True, capture_output=True)
            subprocess.run(f"lsof -t -i :{port} | xargs kill -9 || true", shell=True, capture_output=True)
            await asyncio.sleep(0.5)
        except Exception:
            pass

        enhanced_path = get_enhanced_path()
        omniroute_bin = shutil.which("omniroute", path=enhanced_path) or shutil.which("omnirouter", path=enhanced_path)
        if omniroute_bin:
            cmd = [omniroute_bin, "serve"]
        else:
            npx_bin = shutil.which("npx", path=enhanced_path) or "npx"
            cmd = [npx_bin, "-y", "omniroute", "serve"]

        env = os.environ.copy()
        env["PATH"] = enhanced_path
        log_file = open("/tmp/omniroute_start.log", "a")
        subprocess.Popen(cmd, env=env, stdout=log_file, stderr=log_file, start_new_session=True)

        for _ in range(8):
            await asyncio.sleep(1.0)
            if await check_omniroute_running(base_url):
                return {"message": "OmniRoute se ha iniciado correctamente.", "running": True}

        return {
            "message": "Se envió la orden de inicio para OmniRoute. La conexión se actualizará automáticamente en unos segundos.",
            "running": False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo iniciar OmniRoute automáticamente: {str(e)}")



@app.post("/api/audio/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    try:
        suffix = Path(file.filename or "audio.webm").suffix or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        transcriber = AudioTranscriber()
        transcribed_text = await transcriber.transcribe_audio(tmp_path)

        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)

        return {"transcription": transcribed_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al transcribir audio: {str(e)}")


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
        explorer = IdeaExplorer(llm_client=llm, editorial_memory=editorial_memory)
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
        griller = ArgumentGriller(llm_client=client, editorial_memory=editorial_memory)
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
        planner = ContentPlanner(llm_client=llm, editorial_memory=editorial_memory)
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
        generator = DraftGenerator(llm_client=llm, editorial_memory=editorial_memory)

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
        auditor = VoiceAuditor(llm_client=llm, editorial_memory=editorial_memory)
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
        editor = VoiceEditor(llm_client=llm, editorial_memory=editorial_memory)

        feedback_text = payload.feedback.strip() if payload and payload.feedback and payload.feedback.strip() else "Integrar las notas y modificaciones realizadas directamente en el borrador"

        revised_draft = await editor.revise(
            original_idea=session.original_idea,
            current_draft=session.draft,
            feedback_text=feedback_text,
        )

        session.feedback.append(feedback_text)
        session.revisions.append(revised_draft.content)
        session.draft = revised_draft
        session_manager.save_session(session)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servicio LLM: {str(e)}")


@app.post("/api/profile/extract-tone")
async def extract_profile_tone(payload: ProfileExtractInput):
    try:
        llm = get_llm_client()
        generator = ProfileGenerator(llm_client=llm)
        updated_profile = await generator.update_editorial_profile(payload.samples)
        return {"message": "Perfil editorial actualizado con éxito.", "updated_profile": updated_profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al extraer tono: {str(e)}")


@app.post("/api/ideas/{session_id}/learn-preference", response_model=EditorialSession)
async def learn_editor_preference(session_id: str, payload: LearnPreferenceInput):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    try:
        llm = get_llm_client()
        editor = VoiceEditor(llm_client=llm, editorial_memory=editorial_memory)
        await editor.save_preference_to_profile(payload.user_correction)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar preferencia: {str(e)}")


@app.get("/api/memory")
async def get_editorial_memory():
    return editorial_memory.get_all_memory()


@app.post("/api/memory/preference")
async def add_memory_preference(payload: PreferenceInput):
    editorial_memory.add_preference(payload.category, payload.preference)
    return {"message": "Preferencia guardada correctamente en memoria editorial."}


@app.delete("/api/memory/preference")
async def delete_memory_preference(payload: PreferenceInput):
    success = editorial_memory.delete_preference(payload.category, payload.preference)
    if success:
        return {"message": "Preferencia eliminada correctamente de la memoria."}
    raise HTTPException(status_code=404, detail="La preferencia no fue encontrada en esa categoría.")


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


