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

app = FastAPI(title="Fuera de mi cabeza — Personal Editorial Agent", version="0.1.0")

session_manager = SessionManager()


# DTOs para solicitudes de la API
class AnswersInput(BaseModel):
    answers: list[str]


class DraftRequestInput(BaseModel):
    format: Literal["note", "article"] = "article"
    chosen_title: str | None = None


class RevisionInput(BaseModel):
    feedback: str


# Endpoints de la API
@app.post("/api/ideas", response_model=EditorialSession)
async def create_idea(input_data: IdeaInput):
    session = session_manager.create_session(original_idea=input_data.idea)
    return session


@app.post("/api/ideas/{session_id}/explore", response_model=EditorialSession)
async def explore_idea(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    llm = get_llm_client()
    explorer = IdeaExplorer(llm_client=llm)
    analysis = await explorer.analyze(session.original_idea)

    session.analysis = analysis
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


@app.post("/api/ideas/{session_id}/plan", response_model=EditorialSession)
async def plan_content(session_id: str):
    session = session_manager.get_session(session_id)
    if not session or not session.analysis:
        raise HTTPException(status_code=400, detail="La sesión debe haber completado el análisis previamente")

    llm = get_llm_client()
    planner = ContentPlanner(llm_client=llm)
    plan = await planner.plan(
        original_idea=session.original_idea,
        analysis=session.analysis,
        user_answers=session.user_answers,
    )

    session.content_plan = plan
    session_manager.save_session(session)
    return session


@app.post("/api/ideas/{session_id}/draft", response_model=EditorialSession)
async def generate_draft(session_id: str, payload: DraftRequestInput):
    session = session_manager.get_session(session_id)
    if not session or not session.content_plan:
        raise HTTPException(status_code=400, detail="Se requiere un plan de contenido aprobado antes de generar un borrador")

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


@app.post("/api/ideas/{session_id}/revise", response_model=EditorialSession)
async def revise_draft(session_id: str, payload: RevisionInput):
    session = session_manager.get_session(session_id)
    if not session or not session.draft:
        raise HTTPException(status_code=400, detail="No hay un borrador existente para revisar")

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


@app.get("/api/sessions/{session_id}", response_model=EditorialSession)
async def get_session_details(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return session


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)


# Web UI mínima
WEB_DIR = Path(__file__).resolve().parent / "web"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Fuera de mi cabeza — API lista</h1>")

