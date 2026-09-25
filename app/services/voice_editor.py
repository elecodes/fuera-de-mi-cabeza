import json
from pathlib import Path
from app.llm.client import LLMClient
from app.models.draft import Draft
from app.memory.editorial_memory import EditorialMemory
from app.services.voice_profile import load_voice_profile
from app.services.text_output import strip_code_fences


class VoiceEditor:
    """
    Servicio encargado de editar y revisar el borrador en base al feedback del autor,
    garantizando que el texto mantenga la voz única sin sonar artificial,
    e incluyendo un bucle de aprendizaje continuo para actualizar el perfil editorial y la memoria.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        editorial_memory: EditorialMemory | None = None,
        profile_path: Path | str | None = None,
        prompt_path: Path | str | None = None,
        learn_prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        self.editorial_memory = editorial_memory or EditorialMemory()
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "revise_draft.md"
        self.learn_prompt_path = (
            Path(learn_prompt_path) if learn_prompt_path else base_dir / "app" / "prompts" / "learn_preference.md"
        )

    def _load_profile(self) -> str:
        return load_voice_profile(self.editorial_memory, self.profile_path)


    @staticmethod
    def _detect_intent(draft_content: str, feedback_text: str) -> str:
        fb_lower = feedback_text.lower()
        if any(w in fb_lower for w in ["divide", "dividir", "2 post", "2 párrafos", "partes", "parte 1", "es muy largo", "fraccionar"]):
            return "SPLIT_POST"
        if any(w in fb_lower for w in ["párrafo", "parrafo", "frase", "cambia", "cambiar", "reescribir", "sustituir", "segundo"]):
            return "REWRITE_PARAGRAPH"
        if "[" in draft_content and "]" in draft_content and any(w in draft_content for w in ["Nota:", "nota:", "cambiar", "reemplazar"]):
            return "INTEGRATE_NOTES"
        return "GENERAL_REVISION"

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

        intent = self._detect_intent(current_draft.content, feedback_text)

        if intent == "SPLIT_POST":
            intent_instruction = "INSTRUCCIÓN PRIORITARIA DE FRACCIONAMIENTO: Fracciona el contenido del borrador en 2 entregas independientes (# Parte 1: [Título] y # Parte 2: [Título]). "
        elif intent == "REWRITE_PARAGRAPH":
            intent_instruction = f"INSTRUCCIÓN PRIORITARIA DE REESCRITURA: El autor solicita modificar/sustituir un párrafo o frase concreta ('{feedback_text}'). Ubica el párrafo señalado y REESCRIBELO DIRECTAMENTE IN-PLACE en su posición original dentro del texto, conservando el resto del artículo intacto. "
        elif intent == "INTEGRATE_NOTES":
            intent_instruction = "INSTRUCCIÓN PRIORITARIA DE NOTAS: El borrador contiene comentarios entre corchetes [Nota: ...]. Procesa y consume la nota aplicando la sustitución solicitada y ELIMINA por completo los corchetes y etiquetas [Nota: ...] del borrador final. "
        else:
            intent_instruction = "INSTRUCCIÓN DE REVISIÓN GENERAL: Ajusta el ritmo y la voz según el feedback sin alterar la estructura básica del texto. "

        format_instruction = (
            f"{intent_instruction}Salvo petición explícita de acortar o dividir, mantén la estructura de ARTÍCULO DE SUBSTACK (300 a 600 palabras) con secciones ##. "
            if current_draft.format == "article"
            else f"{intent_instruction}Mantén una extensión compacta tipo Substack Note. "
        )

        # Nota: las reglas aprendidas (editorial_memory) ya están incluidas dentro
        # de `editorial_profile` vía load_voice_profile; no se repiten aquí para
        # no duplicar contenido en el prompt.
        system_prompt = (
            "Eres el editor de voz de 'Fuera de mi cabeza'. "
            "Edita y redacta SIEMPRE en Español de España. "
            f"{format_instruction}"
            "INCORPORA FIELMENTE LAS EXPRESIONES Y MULETILLAS APRENDIDAS DEL AUTOR, "
            "tal como aparecen en el Perfil Editorial y Guía de Voz. "
            "Elimina strictly antítesis ('No es X, es Y'), intros vacías ('En un mundo...'), regla de tres, "
            "afirmaciones cautelosas, metáforas clichés ('brújula, no mapa'), adjetivos inflados, verbos de relleno, "
            "repeticiones de 'profundizar', falsos contrastes ('no obstante'), "
            "entusiasmo artificial, cierres circulares ('En resumen'), "
            "preguntas de transición armadas, emojis decorativos y abuso de rayas (—). "
            "PROHIBIDO adjuntar notas del editor, resúmenes o secciones como '## Revisión Aplicada' al final. "
            "Devuelve ÚNICAMENTE el texto plano revisado, sin JSON, sin título y sin repetir el formato."
        )

        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        content = strip_code_fences(raw_response)
        # El formato y el título del borrador se conservan siempre desde current_draft:
        # a la revisión solo se le pide el contenido, nunca que decida un título nuevo
        # por su cuenta (antes, si el modelo devolvía un título no vacío, lo sustituía
        # sin que el autor lo hubiera pedido).
        return Draft.model_validate({
            "format": current_draft.format,
            "title": current_draft.title,
            "content": content,
        })

    async def save_preference_to_profile(self, user_correction: str) -> str:
        """
        Bucle de aprendizaje continuo: recibe una corrección o preferencia del autor durante la edición,
        sintetiza una regla limpia y la incorpora de forma permanente a data/editorial_profile.md
        y data/editorial_memory.json.
        """
        editorial_profile = self._load_profile()

        # Determinar categoría para la memoria editorial
        fb_lower = user_correction.lower()
        if any(w in fb_lower for w in ["expresión", "muletilla", "frase", "giro", "usar", "decir"]):
            cat = "favorite_expressions"
        elif any(w in fb_lower for w in ["no usar", "evitar", "eliminar", "palabra", "vicio", "tic"]):
            cat = "forbidden_words"
        elif any(w in fb_lower for w in ["ritmo", "oraciones", "largo", "corto", "frases"]):
            cat = "rhythm_rules"
        else:
            cat = "style_rules"

        if not self.learn_prompt_path.exists():
            raise FileNotFoundError(f"No se encontró el template de síntesis en {self.learn_prompt_path}")

        prompt_template = self.learn_prompt_path.read_text(encoding="utf-8")
        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{user_correction}", user_correction)
        )

        system_prompt = (
            "Eres el sintetizador de reglas para el Perfil Editorial de 'Fuera de mi cabeza'. "
            "Responde SIEMPRE con un objeto JSON válido con la estructura solicitada."
        )

        # Se intenta sintetizar la corrección en una regla limpia hasta dos veces.
        # Si la síntesis falla, NUNCA se guarda el comentario en bruto del autor como
        # si fuera una regla: eso es lo que llenó editorial_memory.json de texto sin
        # limpiar en el pasado. Mejor fallar de forma visible que envenenar la memoria.
        synthesized_rule: str | None = None
        last_error: Exception | None = None
        for _ in range(2):
            try:
                raw_response = await self.llm_client.generate(
                    prompt=formatted_prompt,
                    system_prompt=system_prompt,
                )
                clean_json = self._clean_json_output(raw_response)
                data = json.loads(clean_json)
                candidate = data.get("synthesized_rule", "").strip()
                if candidate:
                    synthesized_rule = candidate
                    break
            except Exception as e:
                last_error = e

        if synthesized_rule is None:
            raise RuntimeError(
                "No se pudo sintetizar una regla limpia a partir del feedback. "
                "No se ha guardado nada en la memoria editorial."
            ) from last_error

        note = f"\n\n- **Preferencia aprendida**: {synthesized_rule}\n"
        if self.profile_path:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)
            with self.profile_path.open("a", encoding="utf-8") as fh:
                fh.write(note)

        # Fuente de verdad para lo que se inyecta en los prompts.
        self.editorial_memory.add_preference(category=cat, preference=synthesized_rule)

        return synthesized_rule

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
