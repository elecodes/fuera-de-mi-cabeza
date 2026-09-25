from pathlib import Path
from app.llm.client import LLMClient
from app.models.content_plan import ContentPlan
from app.models.draft import Draft
from app.memory.editorial_memory import EditorialMemory
from app.services.voice_profile import load_voice_profile
from app.services.text_output import strip_code_fences, parse_titled_content


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
        return load_voice_profile(self.editorial_memory, self.profile_path)

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

        # Nota: las reglas aprendidas (editorial_memory) ya están incluidas dentro
        # de `editorial_profile` vía load_voice_profile; no se repiten aquí para
        # no duplicar contenido en el prompt.
        system_prompt = (
            "Eres el redactor de 'Fuera de mi cabeza'. "
            "Redacta el borrador SIEMPRE en Español de España. "
            "INCORPORA FIELMENTE LAS EXPRESIONES, MULETILLAS Y ESTILO APRENDIDO DEL AUTOR, "
            "tal como aparecen en el Perfil Editorial y Guía de Voz. "
            "PROHIBIDO usar tics de IA: antítesis ('No es X, es Y'), intros vacías ('En un mundo...'), regla de tres constante, "
            "afirmaciones sobrecalificadas ('Es importante señalar'), metáforas trilladas ('brújula, no mapa'), autoayuda ('¡Tú puedes!'), "
            "cierres circulares ('En resumen'), preguntas de transición ('¿La trampa?'), emojis decorativos o abusar de rayas (—). "
            "Devuelve únicamente el texto plano de la Note, sin JSON."
        )
        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        content = strip_code_fences(raw_response)
        return Draft.model_validate({"format": "note", "title": None, "content": content})

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

        # Nota: las reglas aprendidas (editorial_memory) ya están incluidas dentro
        # de `editorial_profile` vía load_voice_profile; no se repiten aquí para
        # no duplicar contenido en el prompt.
        system_prompt = (
            "Eres el redactor de 'Fuera de mi cabeza'. "
            "Redacta el borrador SIEMPRE en Español de España. "
            "EXIGENCIA RIGUROSA DE CONCISIÓN Y DENSIDAD (CERO PAJA): Redacta un ARTÍCULO de Substack denso y bien enfocado (entre 300 y 600 palabras). "
            "Es preferible un texto de 350 palabras preciso y memorable que un texto largo inflado con frases de relleno. "
            "INCORPORA FIELMENTE LAS EXPRESIONES, MULETILLAS Y ESTILO APRENDIDO DEL AUTOR, "
            "tal como aparecen en el Perfil Editorial y Guía de Voz. "
            "PROHIBIDO usar tics de IA: antítesis ('No es X, es Y'), intros vacías ('En un mundo...'), regla de tres constante, "
            "afirmaciones sobrecalificadas ('Es importante señalar'), metáforas trilladas ('brújula, no mapa'), autoayuda ('¡Tú puedes!'), "
            "cierres circulares ('En resumen'), preguntas de transición ('¿La trampa?'), emojis decorativos o abusar de rayas (—). "
            "Devuelve el título y el contenido separados por los marcadores ===TITULO=== / ===CONTENIDO===, sin JSON."
        )

        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        parsed_title, content = parse_titled_content(raw_response)
        return Draft.model_validate({
            "format": "article",
            "title": parsed_title or title,
            "content": content,
        })
