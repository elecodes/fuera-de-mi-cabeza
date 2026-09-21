import json
from pathlib import Path
from app.llm.client import LLMClient


class ProfileGenerator:
    """
    Servicio encargado de analizar muestras reales de texto (email, post, newsletter)
    para extraer patrones concretos de tono y generar/actualizar editorial_profile.md.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        profile_path: Path | str | None = None,
        prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "extract_tone.md"

    def _load_prompt_template(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No se encontró el template de prompt en {self.prompt_path}")

    async def generate_profile_from_samples(self, samples: list[str]) -> dict:
        if len(samples) < 1:
            raise ValueError("Se requiere al menos 1 muestra de texto para el extractor de tono.")

        formatted_samples = ""
        for i, sample in enumerate(samples, 1):
            formatted_samples += f"\n### Muestra {i}\n{sample.strip()}\n"

        prompt_template = self._load_prompt_template()
        formatted_prompt = prompt_template.replace("{sample_texts}", formatted_samples)

        system_prompt = (
            "Eres un extractor estricto de tono y perfil editorial. "
            "Responde SIEMPRE con un objeto JSON válido respetando el esquema solicitado."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json_str = self._clean_json_output(raw_response)
        try:
            data = json.loads(clean_json_str)
        except Exception:
            data = {
                "opening_patterns": ["Entradas directas basadas en situaciones reales"],
                "preferred_connectors": ["pero", "de hecho", "la cuestión es"],
                "avoided_patterns": ["Jerga corporativa", "Adjetivos inflados"],
                "humor_and_tone": "Cercano, reflexivo e honesto",
                "cadence_and_rhythm": "Ritmo variable combinando frases cortas con explicaciones matizadas",
                "generated_profile_markdown": raw_response,
            }

        return data

    async def update_editorial_profile(self, samples: list[str]) -> str:
        profile_data = await self.generate_profile_from_samples(samples)
        new_content = profile_data.get("generated_profile_markdown", "")

        if new_content and self.profile_path:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)
            self.profile_path.write_text(new_content, encoding="utf-8")

        return new_content

    @staticmethod
    def _clean_json_output(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text
