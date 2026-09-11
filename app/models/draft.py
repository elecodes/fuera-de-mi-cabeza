from typing import Literal
from pydantic import BaseModel, Field


class Draft(BaseModel):
    format: Literal["note", "article"] = Field(..., description="Formato del borrador")
    title: str | None = Field(default=None, description="Título del contenido (opcional para Note)")
    content: str = Field(..., description="Texto completo del borrador")
