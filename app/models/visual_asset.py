from datetime import datetime, timezone
from pydantic import BaseModel, Field


class VisualAsset(BaseModel):
    id: str = Field(..., description="ID único del asset visual")
    slug: str = Field(..., description="Slug seguro para URL")
    title: str = Field(..., description="Título de la máquina o metáfora")
    concept: str = Field(..., description="Concepto técnico que explica la máquina")
    metaphor: str = Field(..., description="Metáfora física utilizada (ej: balancín de contrapeso, torre de destilación)")
    html_content: str = Field(..., description="HTML autocontenido interactivo con SVG/CSS/JS")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def substack_snippet(self, base_url: str = "") -> str:
        url = f"{base_url.rstrip('/')}/visuals/{self.slug}" if base_url else f"/visuals/{self.slug}"
        return (
            f"> ⚙️ **{self.title}** (*Metáfora: {self.metaphor}*)\n"
            f"> 💡 *[Explorá la máquina interactiva en vivo ↗]({url})*"
        )


class VisualAssetRequest(BaseModel):
    concept: str | None = Field(default=None, description="Concepto específico a ilustrar (opcional, se extrae del borrador si no se indica)")
    title: str | None = Field(default=None, description="Título opcional para el visual")
