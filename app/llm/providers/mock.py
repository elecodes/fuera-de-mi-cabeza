import json
from typing import Callable

DEFAULT_EXPLORE_RESPONSE = {
    "core_idea": "Explorar cómo transformar experiencias e ideas en contenido reflexivo y útil",
    "connected_thoughts": [
        "Sintetizar notas sueltas e ideas en bruto",
        "Estructurar borradores mediante arcos narrativos",
        "Capturar la voz natural del autor sin invenciones"
    ],
    "narrative_arcs": [
        {
            "id": "arc-1",
            "title": "Del Caos de Notas a la Estructura Clara",
            "thought_sequence": [
                "1. Recopilar viñetas e ideas sueltas",
                "2. Conectar conceptos clave mediante preguntas",
                "3. Redactar el borrador definitivo"
            ],
            "rationale": "Permite pasar de pensamientos desordenados a una narrativa lógica y progresiva."
        },
        {
            "id": "arc-2",
            "title": "Construcción Práctica y Aprendizaje Continuo",
            "thought_sequence": [
                "1. Identificar el problema o necesidad de partida",
                "2. Probar la solución de forma directa",
                "3. Extraer lecciones reflexivas para compartir"
            ],
            "rationale": "Ideal para artículos centrados en la experiencia práctica de creación."
        }
    ],
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
    "title": "Convertir ideas en realidad: la brecha entre aprender y construir",
    "content": """# Convertir ideas en realidad: la brecha entre aprender y construir

Llevo bastante tiempo dándole vueltas a una paradoja habitual: la distancia enorme que existe entre acumular conocimientos y sentarse a construir algo real. Es muy fácil caer en la trampa de la preparación infinita. Leemos artículos, guardamos tutoriales, diseñamos diagramas en la cabeza y nos convencemos de que estamos avanzando solo porque estamos ocupados procesando información.

Pero la realidad aparece cuando abres un archivo en blanco y tratas de armar la versión 0.1 de un producto o de un texto. Ahí es donde las ideas abstractas chocan con los problemas prácticos.

## La trampa de la preparación infinita y el espejismo del control

Existe una comodidad innegable en la fase teórica. Mientras una idea permanece en tu cabeza o en un documento de notas, es perfecta. No tiene fallos de arquitectura, no recibe críticas y no requiere lidiar con la fricción del código roto o la frustración de la página en blanco.

Sin embargo, ese exceso de preparación suele ser simplemente miedo disfrazado de rigor. Pensamos que nos falta leer un libro más, probar un framework nuevo o afinar la estructura antes de lanzar. En la práctica, ese ciclo solo aplaza la única actividad que genera aprendizaje verdadero: el contacto directo con la ejecución.

## La importancia de publicar versiones 0.1 imperfectas

Cuando te obligas a cerrar una versión 0.1, el enfoque cambia por completo. Ya no estás intentando resolver todos los escenarios hipotéticos del futuro; estás resolviendo el problema inmediato que tienes delante.

Lo interesante es que los descubrimientos más valiosos casi nunca ocurren durante la planificación. Surgen cuando pones a prueba la primera versión y ves cómo responde. La imperfección inicial no es un fallo del proceso, sino el precio de entrada para construir cosas útiles.

## Un cambio de mentalidad hacia la construcción continua

La cuestión no es dejar de aprender ni actuar de forma impulsiva. El matiz está en alternar rápidamente entre absorber conocimiento y aplicarlo. Aprender un concepto, construir una prueba pequeña, observar el resultado y ajustar a partir de ahí.

Al final, lo que cuenta no es cuántos conceptos dominas en teoría, sino cuántas ideas has logrado sacar de tu cabeza para convertirlas en algo tangible.
"""
}

DEFAULT_REVISION_RESPONSE = {
    "format": "article",
    "title": "Convertir ideas en realidad: la brecha entre aprender y construir",
    "content": """# Convertir ideas en realidad: la brecha entre aprender y construir

Llevo bastante tiempo dándole vueltas a una paradoja habitual: la distancia enorme que existe entre acumular conocimientos y sentarse a construir algo real. Es muy fácil caer en la trampa de la preparación infinita. Leemos artículos, guardamos tutoriales, diseñamos diagramas en la cabeza y nos convencemos de que estamos avanzando solo porque estamos ocupados procesando información.

Pero la realidad aparece cuando abres un archivo en blanco y tratas de armar la versión 0.1 de un producto o de un texto. Ahí es donde las ideas abstractas chocan con los problemas prácticos.

## Lo que ocurre cuando intentamos que todo sea perfecto

Existe una comodidad innegable en la fase teórica. Mientras una idea permanece en tu cabeza o en un documento de notas, es perfecta. No tiene fallos de arquitectura, no recibe críticas y no requiere lidiar con la fricción del código roto o la frustración de la página en blanco.

Sin embargo, ese exceso de preparación suele ser simplemente miedo disfrazado de rigor. Pensamos que nos falta leer un libro más, probar un framework nuevo o afinar la estructura antes de lanzar. En la práctica, ese ciclo solo aplaza la única actividad que genera aprendizaje verdadero: el contacto directo con la ejecución.

## Aprender a través del choque con la realidad

Cuando te obligas a cerrar una versión 0.1, el enfoque cambia por completo. Ya no estás intentando resolver todos los escenarios hipotéticos del futuro; estás resolviendo el problema inmediato que tienes delante.

Lo interesante es que los descubrimientos más valiosos casi nunca ocurren durante la planificación. Surgen cuando pones a prueba la primera versión y ves cómo responde. La imperfección inicial no es un fallo del proceso, sino el precio de entrada para construir cosas útiles.
"""
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

    @staticmethod
    def _clean_idea_summary(idea_text: str) -> str:
        clean = idea_text.replace('[Nota de Voz Grabada]:', '').replace('[Notas de Voz - grabacion_voz.webm]:', '')
        lines = [line.strip() for line in clean.splitlines() if line.strip() and not line.startswith('[')]
        return " ".join(lines) if lines else clean.strip()

    @staticmethod
    def _sanitize_feedback(feedback_text: str) -> str:
        clean = feedback_text.split('banderas de autenticidad:')[0].split('detalles a mejorar:')[0].strip()
        lines = [l.strip(' "\'-*') for l in clean.splitlines() if l.strip()]
        first_line = lines[0] if lines else "ajustar el tono para hacerlo más ameno y cercano"
        return first_line[:120]

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

        prompt_lower = (prompt + " " + (system_prompt or "")).lower()

        # Extraer idea original limpiando marcadores de audio
        idea_raw = ""
        for marker in [
            'Idea Original:',
            'Idea Original del Autor:',
            'Idea / Pensamientos recibidos:',
            'Idea Central y Arco Seleccionado:',
        ]:
            if marker in prompt:
                try:
                    extracted = prompt.split(marker)[1].split('\n')[0].strip(' "\'-*')
                    if extracted and len(extracted) > 3:
                        idea_raw = extracted
                        break
                except Exception:
                    pass

        clean_idea = self._clean_idea_summary(idea_raw)

        # 1. Detección de entrevista Grill (Argument Griller)
        if "argument griller" in prompt_lower or "grill_questions" in prompt_lower or "abogado del diablo" in prompt_lower:
            return json.dumps({
                "grill_questions": [
                    "¿Qué le dirías a alguien que piensa que construir tus propias herramientas quita tiempo de escribir?",
                    "¿En qué proyecto o experiencia concreta sentiste la necesidad de armar estos agentes colaboradores?",
                    "¿En qué casos preferirías no usar esta metodología y escribir de forma tradicional?"
                ]
            }, ensure_ascii=False)

        # 2. Detección de edición y revisión de borrador (Voice Editor)
        elif "voice editor" in prompt_lower or "editor de voz" in prompt_lower or "feedback_text" in prompt_lower or "instrucciones de edición" in prompt_lower:
            feedback_val = ""
            if 'Feedback Recibido del Autor:' in prompt:
                try:
                    feedback_val = prompt.split('Feedback Recibido del Autor:')[1].split('## Instrucciones')[0].strip(' \n"\'')
                except Exception:
                    pass

            current_draft_content = ""
            if 'Borrador Actual:' in prompt:
                try:
                    current_draft_content = prompt.split('Borrador Actual:')[1].split('- **Feedback Recibido')[0].strip(' \n"\'')
                except Exception:
                    pass

            base_content = current_draft_content or DEFAULT_REVISION_RESPONSE["content"]
            clean_lines = [l for l in base_content.splitlines() if not l.startswith("### 📝") and not l.startswith("- **Modificación") and not l.startswith("- **Ajuste") and not l.startswith("- **Voz")]
            clean_base = "\n".join(clean_lines).strip()

            integrated_rev = (
                f"{clean_base}\n\n"
                f"## Ajuste de Tono e Identidad\n\n"
                f"Para responder a tu indicación de hacer el texto más fluido y cercano, eliminamos cualquier formulación "
                f"distante o sobrecargada. La idea es que la lectura avance con soltura conversacional, "
                f"enfocándonos directamente en la experiencia de creación sin adornos innecesarios ni tecnicismos."
            )

            return json.dumps({
                "format": "article",
                "title": "Construir tus propias herramientas: el valor de crear agentes a tu medida",
                "content": integrated_rev
            }, ensure_ascii=False)

        # 3. Detección de Exploración de Ideas
        elif "idea explorer" in prompt_lower or "core_idea" in prompt_lower or "socratic synthesizer" in prompt_lower:
            core = clean_idea or "Crear herramientas propias y agentes colaboradores para Substack"
            explore_res = dict(DEFAULT_EXPLORE_RESPONSE)
            explore_res["core_idea"] = core
            explore_res["connected_thoughts"] = [
                "Construir un flujo de agentes que colaboren en la redacción",
                "Capturar ideas por voz y texto sin perder la voz personal",
                "Entrevistar y estructurar arcos narrativos antes de publicar"
            ]
            return json.dumps(explore_res, ensure_ascii=False)

        # 4. Detección de Plan de Contenido
        elif "content planner" in prompt_lower or "central_message" in prompt_lower or "title_options" in prompt_lower:
            plan_res = dict(DEFAULT_PLAN_RESPONSE)
            plan_res["title_options"] = [
                "Construir tus propias herramientas: el valor de crear agentes a tu medida",
                "De la cabeza al ordenador: cómo colaborar con agentes para redactar en Substack",
                "Sacar las ideas de la cabeza sin perder tu voz"
            ]
            plan_res["central_message"] = "Crear un sistema de agentes colaboradores para convertir notas sueltas en artículos auténticos."
            return json.dumps(plan_res, ensure_ascii=False)

        # 5. Detección de Notas
        elif "generate note" in prompt_lower or "format\": \"note" in prompt_lower:
            return json.dumps({
                "format": "note",
                "title": None,
                "content": "Una reflexión rápida: construir tus propias herramientas no es para complicarte la vida, sino para eliminar la fricción entre tener una idea en la cabeza y verla estructurada sin perder tu voz."
            }, ensure_ascii=False)

        # 6. Detección de Artículos
        elif "generate article" in prompt_lower or "prompt: article" in prompt_lower or "redacta un artículo completo" in prompt_lower or "article" in prompt_lower:
            article_body = (
                "# Construir tus propias herramientas: el valor de crear agentes a tu medida\n\n"
                "Llevo tiempo dándole vueltas a la diferencia entre adaptar nuestro flujo de trabajo a herramientas de terceros "
                "o construir un sistema propio que realmente entienda cómo procesamos las ideas.\n\n"
                "Cuando trabajas en conceptos complejos, el teclado a veces se convierte en un cuello de botella. "
                "Dictar notas de voz, capturar intuiciones al vuelo y permitir que un grupo de agentes colaboren para ordenar ese material "
                "no es una cuestión de automatización vacía: es una forma de mantener la autenticidad y sacar las ideas de la cabeza.\n\n"
                "## De la intuición suelta al sistema articulado\n\n"
                "Lo importante no está en delegar la escritura en la inteligencia artificial, sino en usarla como caja de resonancia. "
                "Un agente editorial no debe inventar historias ni imponer un tono corporativo. Su trabajo es formular las preguntas adecuadas, "
                "desafiar tus premisas mediante entrevistas y estructurar el caos inicial.\n\n"
                "## Conectar piezas sin perder la voz personal\n\n"
                "Al integrar notas habladas y textos libres en un mismo cuaderno digital, se reduce la fricción entre la idea inicial "
                "y el borrador final listo para Substack. Lo verdaderamente valioso es que el resultado siga sonando a ti."
            )

            return json.dumps({
                "format": "article",
                "title": "Construir tus propias herramientas: el valor de crear agentes a tu medida",
                "content": article_body
            }, ensure_ascii=False)

        return json.dumps(DEFAULT_ARTICLE_RESPONSE, ensure_ascii=False)

