from datetime import datetime, timezone
from pydantic import BaseModel, Field
from app.models.analysis import IdeaAnalysis
from app.models.content_plan import ContentPlan
from app.models.draft import Draft


class EditorialSession(BaseModel):
    id: str = Field(..., description="ID único de la sesión editorial")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    original_idea: str = Field(..., description="Idea original ingresada por el usuario")
    analysis: IdeaAnalysis | None = Field(default=None, description="Resultado del análisis de la idea")
    user_answers: list[str] = Field(default_factory=list, description="Respuestas del usuario a las preguntas del análisis")
    content_plan: ContentPlan | None = Field(default=None, description="Plan de contenido aprobado o propuesto")
    draft: Draft | None = Field(default=None, description="Borrador actual generado")
    feedback: list[str] = Field(default_factory=list, description="Historial de feedback provisto por el usuario")
    revisions: list[str] = Field(default_factory=list, description="Historial de revisiones del borrador")
