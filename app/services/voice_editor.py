import json
from pathlib import Path
from app.llm.client import LLMClient
from app.models.draft import Draft


class VoiceEditor:
    """
    Servicio encargado de editar y revisar el borrador en base al feedback del autor,
    garantizando que el texto mantenga la voz única sin sonar artificial,
    e incluyendo un bucle de aprendizaje continuo para actualizar el perfil editorial.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        profile_path: Path | str | None = None,
        prompt_path: Path | str | None = None,
        learn_prompt_path: Path | str | None = None,
    ):
        self.llm_client = llm_client
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"
        self.prompt_path = Path(prompt_path) if prompt_path else base_dir / "app" / "prompts" / "revise_draft.md"
        self.learn_prompt_path = (
            Path(learn_prompt_path) if learn_prompt_path else base_dir / "app" / "prompts" / "learn_preference.md"
        )

    def _load_profile(self) -> str:
        if self.profile_path.exists():
            return self.profile_path.read_text(encoding="utf-8")
        return "Perfil Editorial no especificado."

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
            f"{intent_instruction}Salvo petición explícita de acortar o dividir, mantén la estructura de ARTÍCULO DE SUBSTACK (600 a 1200 palabras) con secciones ##. "
            if current_draft.format == "article"
            else f"{intent_instruction}Mantén una extensión compacta tipo Substack Note. "
        )

        system_prompt = (
            "Eres el editor de voz de 'Fuera de mi cabeza'. "
            "Edita y redacta SIEMPRE en Español de España. "
            f"{format_instruction}"
            "Elimina strictly antítesis ('No es X, es Y'), intros vacías ('En un mundo...'), regla de tres, "
            "afirmaciones cautelosas, metáforas clichés ('brújula, no mapa'), adjetivos inflados, verbos de relleno, "
            "repeticiones de 'profundizar', falsos contrastes ('no obstante'), "
            "entusiasmo artificial, cierres circulares ('En resumen'), "
            "preguntas de transición armadas, emojis decorativos y abuso de rayas (—). "
            "PROHIBIDO adjuntar notas del editor, resúmenes o secciones como '## Revisión Aplicada' al final. Devuelve únicamente el borrador limpio revisado en JSON."
        )

        raw_response = await self.llm_client.generate(prompt=formatted_prompt, system_prompt=system_prompt)

        clean_json_str = self._clean_json_output(raw_response)
        data = json.loads(clean_json_str)
        data["format"] = current_draft.format
        if "title" not in data or not data["title"]:
            data["title"] = current_draft.title
        return Draft.model_validate(data)

    async def save_preference_to_profile(self, user_correction: str) -> str:
        """
        Bucle de aprendizaje continuo: recibe una corrección o preferencia del autor durante la edición,
        sintetiza una regla limpia y la incorpora de forma permanente a data/editorial_profile.md.
        """
        editorial_profile = self._load_profile()
        if not self.learn_prompt_path.exists():
            # Fallback simple si no existe la plantilla
            rule_entry = f"\n- **Preferencia aprendida**: {user_correction.strip()}\n"
            updated_profile = editorial_profile + rule_entry
            if self.profile_path:
                self.profile_path.write_text(updated_profile, encoding="utf-8")
            return updated_profile

        prompt_template = self.learn_prompt_path.read_text(encoding="utf-8")
        formatted_prompt = (
            prompt_template.replace("{editorial_profile}", editorial_profile)
            .replace("{user_correction}", user_correction)
        )

        system_prompt = (
            "Eres el sintetizador de reglas para el Perfil Editorial de 'Fuera de mi cabeza'. "
            "Responde SIEMPRE con un objeto JSON válido con la estructura solicitada."
        )

        raw_response = await self.llm_client.generate(
            prompt=formatted_prompt,
            system_prompt=system_prompt,
        )

        clean_json = self._clean_json_output(raw_response)
        try:
            data = json.loads(clean_json)
            updated_markdown = data.get("updated_profile_markdown")
            synthesized_rule = data.get("synthesized_rule", "")

            if not updated_markdown or len(updated_markdown.strip()) < 50:
                # Si el LLM no devolvió el markdown completo, anexamos la regla sintetizada
                rule_text = synthesized_rule or user_correction
                updated_markdown = editorial_profile + f"\n\n- **Preferencia aprendida**: {rule_text}\n"
        except Exception:
            rule_text = user_correction
            updated_markdown = editorial_profile + f"\n\n- **Preferencia aprendida**: {rule_text}\n"

        if self.profile_path:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)
            self.profile_path.write_text(updated_markdown, encoding="utf-8")

        return updated_markdown

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
