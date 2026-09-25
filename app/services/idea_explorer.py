import json
from pathlib import Path
from app.llm.client import LLMClient
from app.memory.editorial_memory import EditorialMemory
from app.services.voice_profile import load_voice_profile
from app.models.analysis import IdeaAnalysis
from app.services.audio_transcriber import AudioTranscriber


class IdeaExplorer:
    """
    Servicio encargado de analizar la idea inicial del autor (en texto o voz)
    y formular preguntas de profundización sin inventar experiencias personales.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        editorial_memory: EditorialMemory | None = None,
        profile_path: Path | str | None = None,
        prompt_path: Path | str | None = None,
        audio_transcriber: AudioTranscriber | None = None,
    ):
        self.llm_client = llm_client
        self.editorial_memory = editorial_memory
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "explore_idea.md"
        self.audio_transcriber = audio_transcriber or AudioTranscriber()

    def _load_profile(self) -> str:
        return load_voice_profile(self.editorial_memory, self.profile_path)

    def _load_prompt_template(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No se encontró el template de prompt en {self.prompt_path}")

    async def analyze(self, idea: str) -> IdeaAnalysis:
        editorial_profile = self._load_profile()
        prompt_template = self._load_prompt_template()

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{idea}", idea)
        )

        system_prompt = (
            "Eres el editor personal de 'Fuera de mi cabeza'. "
            "Responde y formula SIEMPRE tus respuestas, preguntas y textos en Español de España (castellano peninsular: tú, tienes, etc., sin voseo ni expresiones rioplatenses). "
            "Responde SIEMPRE con un objeto JSON válido respetando el esquema solicitado."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json_str = self._clean_json_output(raw_response)
        data = json.loads(clean_json_str)

        # Enforce max 3 questions rule on Pydantic validation level
        if "questions" in data and isinstance(data["questions"], list):
            data["questions"] = data["questions"][:3]

        return IdeaAnalysis.model_validate(data)

    async def analyze_audio_or_text(self, input_source: Path | str) -> IdeaAnalysis:
        """
        Si el input es un archivo de audio, lo transcribe automáticamente antes de pasar a la etapa EXPLORAR.
        """
        transcribed_text = await self.audio_transcriber.transcribe_if_audio(input_source)
        return await self.analyze(transcribed_text)

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
