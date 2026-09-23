import json
from pathlib import Path
from app.llm.client import LLMClient
from app.models.content_plan import ContentPlan
from app.models.draft import Draft
from app.memory.editorial_memory import EditorialMemory


class DraftGenerator:
    """
    Servicio encargado de redactar el primer borrador (Note o Article)
    respetando estrictamente la voz, muletillas y estilo del autor.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        editorial_memory: EditorialMemory | None = None,
        profile_path: Path | str | None = None,
        note_prompt_path: Path | str | None = None,
        article_prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        self.editorial_memory = editorial_memory or EditorialMemory()
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.note_prompt_path = Path(note_prompt_path) if note_prompt_path else base_dir / "app" / "prompts" / "generate_note.md"
        self.article_prompt_path = Path(article_prompt_path) if article_prompt_path else base_dir / "app" / "prompts" / "generate_article.md"

    def _load_profile(self) -> str:
        profile = ""
        if self.profile_path.exists():
            profile = self.profile_path.read_text(encoding="utf-8")
        else:
            profile = "Perfil Editorial no especificado."

        memory_ctx = self.editorial_memory.get_context()
        if memory_ctx:
            return f"{profile}\n\n{memory_ctx}"
        return profile

    async def generate_note(
        self,
        original_idea: str,
        content_plan: ContentPlan,
        user_answers: list[str],
    ) -> Draft:
        editorial_profile = self._load_profile()
        prompt_template = self.note_prompt_path.read_text(encoding="utf-8")

        formatted_answers = "\n".join(f"- {ans}" for ans in user_answers) if user_answers else "Sin respuestas adicionales."
        formatted_key_points = "\n".join(f"- {kp}" for kp in content_plan.key_points)

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{original_idea}", original_idea)
            .replace("{user_answers}", formatted_answers)
            .replace("{central_message}", content_plan.central_message)
            .replace("{key_points}", formatted_key_points)
        )

        memory_instructions = self.editorial_memory.get_context()
        system_prompt = (
            "Eres el redactor de 'Fuera de mi cabeza'. "
            "Redacta el borrador SIEMPRE en Español de España. "
            "INCORPORA FIELMENTE LAS EXPRESIONES, MULETILLAS Y ESTILO APRENDIDO DEL AUTOR. "
            f"{memory_instructions}\n"
            "PROHIBIDO usar tics de IA: antítesis ('No es X, es Y'), intros vacías ('En un mundo...'), regla de tres constante, "
            "afirmaciones sobrecalificadas ('Es importante señalar'), metáforas trilladas ('brújula, no mapa'), autoayuda ('¡Tú puedes!'), "
            "cierres circulares ('En resumen'), preguntas de transición ('¿La trampa?'), emojis decorativos o abusar de rayas (—). "
            "Genera un borrador en formato JSON."
        )
        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        clean_json_str = self._clean_json_output(raw_response)
        data = json.loads(clean_json_str)
        data["format"] = "note"
        return Draft.model_validate(data)

    async def generate_article(
        self,
        original_idea: str,
        content_plan: ContentPlan,
        user_answers: list[str],
        chosen_title: str | None = None,
    ) -> Draft:
        editorial_profile = self._load_profile()
        prompt_template = self.article_prompt_path.read_text(encoding="utf-8")

        title = chosen_title or (content_plan.title_options[0] if content_plan.title_options else "Sin título")
        formatted_answers = "\n".join(f"- {ans}" for ans in user_answers) if user_answers else "Sin respuestas adicionales."
        formatted_key_points = "\n".join(f"- {kp}" for kp in content_plan.key_points)

        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{original_idea}", original_idea)
            .replace("{user_answers}", formatted_answers)
            .replace("{chosen_title}", title)
            .replace("{central_message}", content_plan.central_message)
            .replace("{opening_direction}", content_plan.opening_direction)
            .replace("{key_points}", formatted_key_points)
            .replace("{ending_direction}", content_plan.ending_direction)
        )

        memory_instructions = self.editorial_memory.get_context()
        system_prompt = (
            "Eres el redactor de 'Fuera de mi cabeza'. "
            "Redacta el borrador SIEMPRE en Español de España. "
            "EXIGENCIA RIGUROSA DE CONCISIÓN Y DENSIDAD (CERO PAJA): Redacta un ARTÍCULO de Substack denso y bien enfocado (entre 300 y 600 palabras). "
            "Es preferible un texto de 350 palabras preciso y memorable que un texto largo inflado con frases de relleno. "
            "INCORPORA FIELMENTE LAS EXPRESIONES, MULETILLAS Y ESTILO APRENDIDO DEL AUTOR. "
            f"{memory_instructions}\n"
            "PROHIBIDO usar tics de IA: antítesis ('No es X, es Y'), intros vacías ('En un mundo...'), regla de tres constante, "
            "afirmaciones sobrecalificadas ('Es importante señalar'), metáforas trilladas ('brújula, no mapa'), autoayuda ('¡Tú puedes!'), "
            "cierres circulares ('En resumen'), preguntas de transición ('¿La trampa?'), emojis decorativos o abusar de rayas (—). "
            "Genera un borrador de artículo en formato JSON."
        )

        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        clean_json_str = self._clean_json_output(raw_response)
        data = json.loads(clean_json_str)
        data["format"] = "article"
        if not data.get("title"):
            data["title"] = title
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
