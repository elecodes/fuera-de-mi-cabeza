from pydantic import BaseModel, Field


class IdeaInput(BaseModel):
    idea: str = Field(..., min_length=1, description="La idea, pensamientos libres, viñetas o texto introducido por el usuario")
    raw_thoughts: list[str] = Field(default_factory=list, description="Lista opcional de fragmentos o viñetas individuales")
