import re
import uuid
import unicodedata
from pathlib import Path
from app.llm.client import LLMClient
from app.models.visual_asset import VisualAsset
from app.services.tracer import traced_generate


def slugify(text: str) -> str:
    """Convierte texto en un slug seguro para URLs."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", text)


def parse_anatomy_response(response: str, default_concept: str) -> tuple[str, str, str]:
    """
    Parsea la respuesta del LLM separada por marcadores:
    ===TITULO===
    ===METAFORA===
    ===HTML===
    """
    title = default_concept[:50]
    metaphor = "Mecanismo interactivo"
    html_content = ""

    if "===TITULO===" in response and "===METAFORA===" in response and "===HTML===" in response:
        parts = response.split("===TITULO===")[1]
        t_part, rest = parts.split("===METAFORA===", 1)
        m_part, h_part = rest.split("===HTML===", 1)

        title = t_part.strip() or title
        metaphor = m_part.strip() or metaphor
        html_content = h_part.strip()
    else:
        # Fallback si el LLM no usó los marcadores exactos
        html_content = response.strip()

    # Limpiar posibles bloques de código markdown
    if html_content.startswith("```html"):
        html_content = html_content[7:]
    elif html_content.startswith("```"):
        html_content = html_content[3:]

    if html_content.endswith("```"):
        html_content = html_content[:-3]

    html_content = html_content.strip()

    # Si por alguna razón el HTML quedó vacío, proveer un esqueleto de fallback
    if not html_content:
        html_content = (
            f"<!DOCTYPE html><html><head><meta charset='UTF-8'><title>{title}</title></head>"
            f"<body style='background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:2rem;'>"
            f"<h1>{title}</h1><p>Metáfora: {metaphor}</p></body></html>"
        )

    return title, metaphor, html_content


class AnatomyGenerator:
    """
    Servicio encargado de generar máquinas conceptuales interactivas (assets visuales)
    basadas en la filosofía de Anatomy ('The object is the explanation').
    """

    def __init__(
        self,
        llm_client: LLMClient,
        visuals_dir: Path | str | None = None,
        prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.visuals_dir = Path(visuals_dir) if visuals_dir else base_dir / "data" / "visuals"
        self.visuals_dir.mkdir(parents=True, exist_ok=True)
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "anatomy_prompt.md"

    async def generate_visual(
        self,
        concept: str,
        title: str | None = None,
        context: str | None = None,
    ) -> VisualAsset:
        template = self.prompt_path.read_text(encoding="utf-8")
        prompt = template.replace("{concept}", concept).replace(
            "{context}", context or "Sin contexto editorial adicional."
        )

        response = await traced_generate(
            self.llm_client,
            step="anatomy_visual",
            prompt=prompt,
            system_prompt="Sos un diseñador técnico mecánico de Anatomy. Generás máquinas isométricas tangibles en HTML interactivo.",
        )

        parsed_title, metaphor, html_content = parse_anatomy_response(response, default_concept=concept)
        final_title = title or parsed_title

        short_id = uuid.uuid4().hex[:8]
        slug_base = slugify(final_title) or "anatomy-machine"
        slug = f"{slug_base}-{short_id}"

        # Guardar archivo HTML en el directorio de visuals
        file_path = self.visuals_dir / f"{slug}.html"
        file_path.write_text(html_content, encoding="utf-8")

        return VisualAsset(
            id=f"vis-{short_id}",
            slug=slug,
            title=final_title,
            concept=concept,
            metaphor=metaphor,
            html_content=html_content,
        )

    def get_visual_html(self, slug: str) -> str | None:
        """Recupera el contenido HTML de un visual existente por su slug."""
        file_path = self.visuals_dir / f"{slug}.html"
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return None
