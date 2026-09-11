from typing import Literal
from pydantic import BaseModel, Field


class IdeaAnalysis(BaseModel):
    core_idea: str = Field(..., description="Resumen conciso del núcleo de lo que se intenta explorar")
    possible_angles: list[str] = Field(..., min_length=1, description="Enfoques o ángulos posibles para abordar la idea")
    potential_audience: str = Field(..., description="Público objetivo potencial")
    emotional_tone: str = Field(..., description="Tono emocional predominante")
    recommended_format: Literal["note", "article", "both"] = Field(..., description="Formato recomendado: note, article o both")
    questions: list[str] = Field(..., max_length=3, description="Máximo 3 preguntas para profundizar sin inventar experiencias")
