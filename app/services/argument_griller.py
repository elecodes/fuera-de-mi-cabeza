import json
from pathlib import Path
from app.llm.client import LLMClient


class ArgumentGriller:
    """
    Servicio de entrevista adversarial (Grill My Argument) que formula
    3 preguntas intensivas para desafiar premisas antes de redactar artículos.
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
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "grill_argument.md"

    def _load_profile(self) -> str:
        if self.profile_path.exists():
            return self.profile_path.read_text(encoding="utf-8")
        return "Perfil Editorial no especificado."

    def _load_prompt_template(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No se encontró el template de prompt en {self.prompt_path}")

    async def generate_grill_questions(
        self,
        idea: str,
        arc_title: str,
        thought_sequence: list[str],
    ) -> list[str]:
        editorial_profile = self._load_profile()
        prompt_template = self._load_prompt_template()

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{idea}", idea)
            .replace("{arc_title}", arc_title)
            .replace("{thought_sequence}", json.dumps(thought_sequence, ensure_ascii=False))
        )

        system_prompt = (
            "Eres el cuestionador crítico y abogado del diablo de 'Fuera de mi cabeza'. "
            "Responde en Español de España (castellano peninsular) devolviendo un objeto JSON válido."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json = self._clean_json_output(raw_response)
        try:
            data = json.loads(clean_json)
            questions = data.get("grill_questions", [])
            return questions[:3]
        except Exception:
            return [
                "¿Qué contra-argumento principal le harías a tu postura?",
                "¿En qué vivencia personal específica comprobaste esta idea?",
                "¿En qué casos no aplicaría esta reflexión?"
            ]

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
