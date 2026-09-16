from typing import Literal
from pydantic import BaseModel, Field


class NarrativeArc(BaseModel):
    id: str = Field(..., description="Identificador único del arco narrativo (ej. arc-1)")
    title: str = Field(..., description="Título o enfoque representativo de esta secuencia")
    thought_sequence: list[str] = Field(..., description="Pasos u orden lógico sugerido para conectar los pensamientos")
    rationale: str = Field(..., description="Explicación de por qué esta secuencia ayuda a conectar las ideas de forma natural")


class IdeaAnalysis(BaseModel):
    core_idea: str = Field(..., description="Resumen conciso del núcleo de lo que se intenta explorar")
    connected_thoughts: list[str] = Field(default_factory=list, description="Fragmentos o ideas individuales identificadas y conectadas")
    narrative_arcs: list[NarrativeArc] = Field(default_factory=list, description="Arcos o secuencias sugeridas para ordenar los pensamientos")
    possible_angles: list[str] = Field(..., min_length=1, description="Enfoques o ángulos posibles para abordar la idea")
    potential_audience: str = Field(..., description="Público objetivo potencial")
    emotional_tone: str = Field(..., description="Tono emocional predominante")
    recommended_format: Literal["note", "article", "both"] = Field(..., description="Formato recomendado: note, article o both")
    questions: list[str] = Field(..., max_length=3, description="Máximo 3 preguntas para profundizar sin inventar experiencias")
