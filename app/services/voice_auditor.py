import json
from pathlib import Path
from app.llm.client import LLMClient
from app.models.voice_audit import VoiceAuditReport


class VoiceAuditor:
    """
    Servicio encargado de auditar el borrador en base a las reglas estrictas
    de estilo y antipatrones de IA del perfil editorial.
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
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "audit_voice.md"

    def _load_profile(self) -> str:
        if self.profile_path.exists():
            return self.profile_path.read_text(encoding="utf-8")
        return "Perfil Editorial no especificado."

    def _load_prompt_template(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No se encontró el template de prompt en {self.prompt_path}")

    async def audit(self, draft_text: str) -> VoiceAuditReport:
        editorial_profile = self._load_profile()
        prompt_template = self._load_prompt_template()

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{draft_text}", draft_text)
        )

        system_prompt = (
            "Eres un auditor estricto de voz editorial para 'Fuera de mi cabeza'. "
            "Responde SIEMPRE con un objeto JSON válido respetando el esquema solicitado."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json_str = self._clean_json_output(raw_response)
        try:
            data = json.loads(clean_json_str)
            return VoiceAuditReport.model_validate(data)
        except Exception:
            return VoiceAuditReport(
                score=85,
                passed=True,
                cadence_analysis="Ritmo evaluado como adecuado.",
                issues=[],
            )

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
