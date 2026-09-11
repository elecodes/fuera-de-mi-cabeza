import json
from typing import Callable

DEFAULT_EXPLORE_RESPONSE = {
    "core_idea": "Explorar cómo transformar experiencias e ideas en contenido reflexivo y útil",
    "possible_angles": [
        "El choque entre la teoría y la construcción real",
        "Aprender haciendo: de la parálisis a la versión 0.1",
    ],
    "potential_audience": "Desarrolladores, creativos y personas interesadas en tecnología e IA",
    "emotional_tone": "Reflexivo, honesto y curioso",
    "recommended_format": "article",
    "questions": [
        "¿Qué experiencia concreta o proyecto reciente detonó esta idea?",
        "¿Qué es lo principal que te gustaría descubrir o comunicar a través de este texto?",
    ],
}

DEFAULT_PLAN_RESPONSE = {
    "format": "article",
    "title_options": [
        "Convertir ideas en realidad",
        "Reflexiones fuera de mi cabeza",
        "De la teoría a la versión 0.1",
    ],
    "central_message": "Construir cosas reales requiere priorizar la práctica y aprender de la experiencia.",
    "opening_direction": "Iniciar con una experiencia sincera sobre el proceso de creación.",
    "key_points": [
        "La diferencia entre consumir información y construir proyectos",
        "Aceptar la incertidumbre en el proceso creativo",
        "Pasos prácticos para pasar de la idea a la ejecución",
    ],
    "ending_direction": "Cierre abierto y sutil sin moralejas pretenciosas.",
}

DEFAULT_NOTE_RESPONSE = {
    "format": "note",
    "title": None,
    "content": "Una reflexión breve: a veces nos quedamos atascados refinando ideas en la cabeza. El verdadero aprendizaje ocurre cuando lanzamos una versión inicial y la ponemos a prueba en el mundo real.",
}

DEFAULT_ARTICLE_RESPONSE = {
    "format": "article",
    "title": "Convertir ideas en realidad",
    "content": "# Convertir ideas en realidad\n\nLlevo tiempo pensando en la brecha entre saber algo y hacerlo real. A menudo nos preparamos interminablemente antes de dar el primer paso.\n\n## La trampa de la preparación infinita\n\nEs fácil sentir que necesitamos aprender un poco más antes de empezar. Pero construir es el mejor método de aprendizaje que existe.\n\n## Conclusión\n\nNo se trata de tener todas las respuestas desde el principio, sino de empezar a construir.",
}

DEFAULT_REVISION_RESPONSE = {
    "format": "article",
    "title": "Convertir ideas en realidad",
    "content": "# Convertir ideas en realidad (Versión revisada)\n\nLlevo tiempo pensando en la brecha entre saber algo y hacerlo real. Quería compartir esta reflexión con una voz más cercana y directa.\n\n## Lo que aprendí construyendo\n\nEs fácil sentir que necesitamos aprender un poco más antes de empezar...",
}


class MockLLMClient:
    """
    Cliente LLM simulado para tests unitarios y ejecución local sin API Key.
    """

    def __init__(
        self,
        default_response: str | None = None,
        response_factory: Callable[[str, str | None], str] | None = None,
    ):
        self.default_response = default_response
        self.response_factory = response_factory
        self.call_history: list[dict[str, str | None]] = []

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        self.call_history.append({"prompt": prompt, "system_prompt": system_prompt})
        if self.response_factory:
            return self.response_factory(prompt, system_prompt)
        if self.default_response is not None:
            return self.default_response

        # Detección inteligente según el contenido del prompt
        prompt_lower = (prompt + " " + (system_prompt or "")).lower()

        if "idea explorer" in prompt_lower or "core_idea" in prompt_lower:
            return json.dumps(DEFAULT_EXPLORE_RESPONSE, ensure_ascii=False)
        elif "content planner" in prompt_lower or "central_message" in prompt_lower:
            return json.dumps(DEFAULT_PLAN_RESPONSE, ensure_ascii=False)
        elif "generate note" in prompt_lower or "format\": \"note" in prompt_lower:
            return json.dumps(DEFAULT_NOTE_RESPONSE, ensure_ascii=False)
        elif "voice editor" in prompt_lower or "feedback_text" in prompt_lower:
            return json.dumps(DEFAULT_REVISION_RESPONSE, ensure_ascii=False)
        elif "generate article" in prompt_lower or "article" in prompt_lower:
            return json.dumps(DEFAULT_ARTICLE_RESPONSE, ensure_ascii=False)

        return "{}"

