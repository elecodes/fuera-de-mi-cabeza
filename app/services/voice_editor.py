import json
from pathlib import Path
from app.llm.client import LLMClient
from app.models.draft import Draft


class VoiceEditor:
    """
    Servicio encargado de editar y revisar el borrador en base al feedback del autor,
    garantizando que el texto mantenga la voz única sin sonar artificial.
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
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "revise_draft.md"

    def _load_profile(self) -> str:
        if self.profile_path.exists():
            return self.profile_path.read_text(encoding="utf-8")
        return "Perfil Editorial no especificado."

    async def revise(
        self,
        original_idea: str,
        current_draft: Draft,
        feedback_text: str,
    ) -> Draft:
        editorial_profile = self._load_profile()
        prompt_template = self.prompt_path.read_text(encoding="utf-8")

        title_placeholder = current_draft.title or ""

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{original_idea}", original_idea)
            .replace("{current_draft}", current_draft.content)
            .replace("{feedback_text}", feedback_text)
            .replace("{format}", current_draft.format)
            .replace("{title_placeholder}", title_placeholder)
        )

        system_prompt = (
            "Sos el editor de voz de 'Fuera de mi cabeza'. "
            "Aplica el feedback recibido y devuelve un borrador revisado en JSON."
        )

        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        clean_json_str = self._clean_json_output(raw_response)
        data = json.loads(clean_json_str)
        data["format"] = current_draft.format
        if current_draft.title and not data.get("title"):
            data["title"] = current_draft.title
        return Draft.model_validate(data)

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
