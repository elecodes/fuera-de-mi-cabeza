import json
from pathlib import Path
from app.llm.client import LLMClient
from app.models.analysis import IdeaAnalysis, NarrativeArc
from app.models.content_plan import ContentPlan
from app.memory.editorial_memory import EditorialMemory
from app.services.voice_profile import load_voice_profile


class ContentPlanner:
    """
    Servicio que transforma la idea, su análisis, la secuencia narrativa elegida
    y las respuestas del usuario en un plan de contenido (ContentPlan).
    """

    def __init__(
        self,
        llm_client: LLMClient,
        editorial_memory: EditorialMemory | None = None,
        profile_path: Path | str | None = None,
        prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        self.editorial_memory = editorial_memory or EditorialMemory()
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "content_plan.md"

    def _load_profile(self) -> str:
        return load_voice_profile(self.editorial_memory, self.profile_path)


    def _load_prompt_template(self) -> str:
        if self.prompt_path.exists():
            return self.prompt_path.read_text(encoding="utf-8")
        raise FileNotFoundError(f"No se encontró el template de prompt en {self.prompt_path}")

    async def plan(
        self,
        original_idea: str,
        analysis: IdeaAnalysis,
        user_answers: list[str],
        selected_arc: NarrativeArc | None = None,
        grill_answers: list[str] | None = None,
    ) -> ContentPlan:
        editorial_profile = self._load_profile()
        prompt_template = self._load_prompt_template()

        all_answers = list(user_answers)
        if grill_answers:
            all_answers.append("\n--- Respuestas del Modo Grill (Entrevista Adversarial) ---")
            all_answers.extend(grill_answers)

        formatted_answers = "\n".join(f"- {ans}" for ans in all_answers) if all_answers else "Sin respuestas adicionales."

        selected_arc_info = "Sin secuencia preferida seleccionada previamente."
        if selected_arc:
            seq = " -> ".join(selected_arc.thought_sequence)
            selected_arc_info = f"Título del Arco: {selected_arc.title}\nSecuencia: {seq}\nJustificación: {selected_arc.rationale}"

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{original_idea}", original_idea)
            .replace("{core_idea}", analysis.core_idea)
            .replace("{emotional_tone}", analysis.emotional_tone)
            .replace("{recommended_format}", analysis.recommended_format)
            .replace("{selected_arc_info}", selected_arc_info)
            .replace("{user_answers}", formatted_answers)
        )

        memory_instructions = self.editorial_memory.get_context()
        system_prompt = (
            "Eres el planificador editorial de 'Fuera de mi cabeza'. "
            "Escribe SIEMPRE en Español de España (castellano peninsular: tú, tienes, etc., sin voseo ni modismos argentinos). "
            f"{memory_instructions}\n"
            "Responde SIEMPRE con un objeto JSON válido con la estructura solicitada."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json_str = self._clean_json_output(raw_response)
        data = json.loads(clean_json_str)

        if "title_options" in data and isinstance(data["title_options"], list):
            data["title_options"] = data["title_options"][:3]
        if "key_points" in data and isinstance(data["key_points"], list):
            data["key_points"] = data["key_points"][:5]

        return ContentPlan.model_validate(data)

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
