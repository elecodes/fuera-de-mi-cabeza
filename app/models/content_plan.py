from typing import Literal
from pydantic import BaseModel, Field


class ContentPlan(BaseModel):
    format: Literal["note", "article"] = Field(..., description="Formato del contenido: note o article")
    title_options: list[str] = Field(..., max_length=3, description="Máximo 3 opciones de título")
    central_message: str = Field(..., description="Mensaje central claro en una oración")
    opening_direction: str = Field(..., description="Dirección o gancho inicial")
    key_points: list[str] = Field(..., max_length=5, description="Entre 3 y 5 puntos principales")
    ending_direction: str = Field(..., description="Dirección de cierre o reflexión final")
