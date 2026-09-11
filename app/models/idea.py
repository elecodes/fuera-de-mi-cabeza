from pydantic import BaseModel, Field


class IdeaInput(BaseModel):
    idea: str = Field(..., min_length=1, description="La idea o pensamiento libre introducido por el usuario")
