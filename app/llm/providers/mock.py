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
        "¿Qué hecho, proyecto o conversación específica de esta semana detonó esta intuición?",
        "Mencionas la importancia de esto, pero ¿en qué momento exacto chocaste con la contradicción o la fricción práctica?",
        "¿Qué fue lo más difícil de admitir o qué costo tuvo tomar este camino en lugar de la opción más fácil?"
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
        lines = []
        import re
        for line in clean.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith('['):
                continue
            cleaned_line = re.sub(r'^(?:[-*•]\s*|\d+\.\s*|(?:Pensamiento|Reflexión|Idea|Nota)\s*\d*:?\s*)', '', line_str, flags=re.IGNORECASE).strip()
            if cleaned_line:
                lines.append(cleaned_line)
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
            if 'Borrador Actual' in prompt:
                try:
                    after_marker = prompt.split('Borrador Actual')[1]
                    raw_content = after_marker.split('- **Feedback Recibido')[0]
                    # Limpiar encabezados como '(incluye modificaciones directas y notas del autor):' o ':'
                    lines = raw_content.splitlines()
                    cleaned_lines = []
                    for line in lines:
                        if line.strip().startswith('(') or line.strip() == ':' or line.strip().startswith('**:'):
                            continue
                        cleaned_lines.append(line)
                    current_draft_content = "\n".join(cleaned_lines).strip()
                    if current_draft_content.startswith(':'):
                        current_draft_content = current_draft_content[1:].strip()
                except Exception:
                    pass

            base_content = current_draft_content or DEFAULT_REVISION_RESPONSE["content"]
            clean_lines = [l for l in base_content.splitlines() if not l.startswith("### 📝") and not l.startswith("- **Modificación") and not l.startswith("- **Ajuste") and not l.startswith("- **Voz")]
            raw_base = "\n".join(clean_lines).strip()

            # Procesar y eliminar etiquetas inline entre corchetes [Nota: ...] o [...]
            import re
            clean_base = re.sub(r'\[(?:Nota:?|nota:?|cambiar:?|reemplazar:?)?\s*([^\]]+)\]', r'\1 (frase reescrita según nota)', raw_base)
            clean_base = re.sub(r'\[[^\]]+\]', '', clean_base).strip()

            sanitized_fb = self._sanitize_feedback(feedback_val) if feedback_val else "Ajuste de tono e identidad"
            fb_lower = feedback_val.lower()

            if any(term in fb_lower for term in ["divide", "dividir", "2 post", "2 párrafos", "partes", "parte 1", "es muy largo", "acortar"]):
                # Fraccionar el texto base en 2 entregas diferenciadas
                paragraphs = [p.strip() for p in clean_base.split("\n\n") if p.strip()]
                half = max(1, len(paragraphs) // 2)
                part1_text = "\n\n".join(paragraphs[:half])
                part2_text = "\n\n".join(paragraphs[half:]) if half < len(paragraphs) else "Continúa la segunda parte con las reflexiones de cierre..."

                integrated_rev = (
                    f"# Parte 1: Construir tus propias herramientas (Entrega I)\n\n"
                    f"{part1_text}\n\n"
                    f"---\n\n"
                    f"# Parte 2: De la intuición al sistema articulado (Entrega II)\n\n"
                    f"{part2_text}\n\n"
                    f"*Nota del Editor: El post original ha sido dividido en 2 entregas independientes según tu indicación.*"
                )
            else:
                paragraphs = [p.strip() for p in clean_base.split("\n\n") if p.strip()]
                if len(paragraphs) >= 2 and any(k in fb_lower for k in ["párrafo", "parrafo", "frase", "cambia", "cambiar", "reescribir", "segundo"]):
                    # Modificar in-place el párrafo indicado dentro del texto
                    target_idx = 1 if len(paragraphs) > 1 else 0
                    paragraphs[target_idx] = f"{paragraphs[target_idx]} (Párrafo reescrito según la indicación: '{sanitized_fb}')."
                    integrated_rev = "\n\n".join(paragraphs)
                elif paragraphs and any(k in fb_lower for k in ["párrafo", "parrafo", "frase", "cambia", "cambiar", "reescribir"]):
                    paragraphs[0] = f"{paragraphs[0]} (Párrafo modificado según la indicación: '{sanitized_fb}')."
                    integrated_rev = "\n\n".join(paragraphs)
                else:
                    integrated_rev = clean_base

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
            topic = clean_idea if clean_idea else "esta reflexión"
            title_1 = f"Reflexiones sobre {topic.lower()[:50]}" if len(topic) > 5 else "Reflexiones fuera de mi cabeza"
            title_2 = f"De la idea a la práctica: {topic.lower()[:45]}" if len(topic) > 5 else "De la teoría a la versión 0.1"
            title_3 = f"Lo que aprendí sobre {topic.lower()[:40]}" if len(topic) > 5 else "Aprender construyendo cosas reales"

            return json.dumps({
                "format": "article",
                "title_options": [title_1, title_2, title_3],
                "central_message": f"Profundizar en {topic} conectando experiencias reales y evitando simplificaciones vacías.",
                "opening_direction": f"Iniciar con una observación directa y sincera sobre {topic}.",
                "key_points": [
                    f"El contexto inicial y por qué nos preocupa este tema: {topic}",
                    "Las fricciones prácticas y dudas que surgen al intentar aplicarlo",
                    "Una conclusión reflexiva para seguir explorando con criterio propio"
                ],
                "ending_direction": "Cierre abierto y sutil sin moralejas pretenciosas."
            }, ensure_ascii=False)

        # 5. Detección de Notas
        elif "generate note" in prompt_lower or 'format": "note' in prompt_lower or "píldora reflexiva" in prompt_lower:
            key_points_text = ""
            if "Puntos Clave:" in prompt:
                try:
                    after_kp = prompt.split("Puntos Clave:")[1]
                    key_points_text = after_kp.split("##")[0].split("Respuestas del Autor")[0].strip()
                except Exception:
                    pass

            answers_text = ""
            if "Respuestas del Autor:" in prompt:
                try:
                    after_ans = prompt.split("Respuestas del Autor:")[1]
                    answers_text = after_ans.split("##")[0].strip()
                except Exception:
                    pass

            topic = clean_idea if clean_idea else "esta reflexión"

            import re
            kp_lines = [re.sub(r'^(?:[-*•]\s*|\d+\.\s*|(?:Pensamiento|Reflexión|Idea)\s*\d*:?\s*)', '', l, flags=re.IGNORECASE).strip() for l in key_points_text.splitlines() if l.strip()]

            p1 = f"Al pararme a analizar {topic.lower() if topic[0].isupper() else topic}, queda claro que las intuiciones iniciales suelen necesitar el filtro de la práctica. En el papel todo parece encajar, pero el verdadero valor aparece cuando observamos el comportamiento real."

            if kp_lines:
                p2 = f"En la práctica, {kp_lines[0].lower() if kp_lines[0][0].isupper() else kp_lines[0]}. " + (f"Además, {kp_lines[1].lower() if kp_lines[1][0].isupper() else kp_lines[1]}." if len(kp_lines) > 1 else "Ahí es donde se aprende a ajustar sobre la marcha sin quedarse atrapado en supuestos.")
            else:
                p2 = "La cuestión es que acumular ideas en la cabeza no sirve de nada si no nos atrevemos a probarlas. La fricción inicial no es un problema del proceso, sino el precio de entrada para aprender algo útil."

            if answers_text and "Sin respuestas" not in answers_text and len(answers_text) > 3:
                clean_ans = answers_text.replace('\n', ' ').strip('- *')
                p3 = f"Al responder a estas preguntas, el escenario se aclara: {clean_ans}. Sacar estos pensamientos de la cabeza es el primer paso para construir con criterio propio."
            else:
                p3 = "Al final, sacar estos pensamientos de la cabeza y ponerlos a prueba es lo único que nos permite avanzar con criterio propio."

            note_body = f"{p1}\n\n{p2}\n\n{p3}"

            return json.dumps({
                "format": "note",
                "title": None,
                "content": note_body
            }, ensure_ascii=False)

        # 6. Detección de Artículos
        elif "generate article" in prompt_lower or "prompt: article" in prompt_lower or "redacta un artículo completo" in prompt_lower or "article" in prompt_lower:
            title_val = ""
            for marker in ["Título Elegido / Asignado:", "Título Elegido:", "chosen_title:", "Título del Artículo:"]:
                if marker in prompt:
                    try:
                        title_val = prompt.split(marker)[1].split('\n')[0].strip(' "\'-*')
                        if title_val and len(title_val) > 2:
                            break
                    except Exception:
                        pass

            if not title_val or title_val == "Sin título":
                title_val = f"Reflexiones sobre {clean_idea[:50]}" if clean_idea else "Reflexiones fuera de mi cabeza"

            message_val = ""
            if "Mensaje Central:" in prompt:
                try:
                    message_val = prompt.split("Mensaje Central:")[1].split('\n')[0].strip(' "\'-*')
                except Exception:
                    pass

            key_points_text = ""
            if "Puntos Clave a Desarrollar:" in prompt:
                try:
                    after_kp = prompt.split("Puntos Clave a Desarrollar:")[1]
                    key_points_text = after_kp.split("##")[0].split("Respuestas del Autor")[0].strip()
                except Exception:
                    pass

            answers_text = ""
            if "Respuestas del Autor a Preguntas Socráticas:" in prompt:
                try:
                    after_ans = prompt.split("Respuestas del Autor a Preguntas Socráticas:")[1]
                    answers_text = after_ans.split("##")[0].strip()
                except Exception:
                    pass

            idea_text = clean_idea or "esta reflexión"
            
            import re
            clean_title = re.sub(r'^(?:Reflexiones sobre\s*)+', 'Reflexiones sobre ', title_val, flags=re.IGNORECASE)
            clean_title = re.sub(r'^(?:[-*•]\s*|\d+\.\s*|(?:Pensamiento|Reflexión|Idea)\s*\d*:?\s*)', '', clean_title, flags=re.IGNORECASE).strip()
            if clean_title:
                clean_title = clean_title[0].upper() + clean_title[1:]

            openings = [
                f"A veces la mejor manera de entender un problema es ponerlo por escrito. Últimamente he estado pensando sobre {idea_text.lower() if idea_text[0].isupper() else idea_text}.",
                f"Hay una cuestión sobre {idea_text.lower()[:80] if len(idea_text) > 5 else 'este tema'} que nos obliga a mirar más allá de la teoría. Cuando te paras a analizarlo con calma, la distancia entre lo que pensamos y lo que ejecutamos se vuelve evidente.",
                f"En cualquier proceso de creación, las intuiciones más valiosas surgen cuando atamos cabos entre ideas que parecían sueltas. Hoy quiero profundizar en {idea_text.lower()[:80] if len(idea_text) > 5 else 'esta reflexión'}."
            ]
            opening_sentence = openings[abs(hash(idea_text)) % len(openings)]

            kp_lines = [re.sub(r'^(?:[-*•]\s*|\d+\.\s*|(?:Pensamiento|Reflexión|Idea)\s*\d*:?\s*)', '', l, flags=re.IGNORECASE).strip() for l in key_points_text.splitlines() if l.strip()]
            sec1_title = kp_lines[0] if len(kp_lines) > 0 and len(kp_lines[0]) > 3 else "De la observación inicial a la práctica"
            sec2_title = kp_lines[1] if len(kp_lines) > 1 and len(kp_lines[1]) > 3 else "Aprendizajes y tensiones durante el proceso"
            sec3_title = kp_lines[2] if len(kp_lines) > 2 and len(kp_lines[2]) > 3 else "Un cambio de perspectiva con criterio propio"

            ans_section = f"\n\nAl responder a las preguntas de profundización, el escenario se aclara: {answers_text.replace(chr(10), ' ')}" if answers_text and "Sin respuestas" not in answers_text and len(answers_text) > 3 else ""

            article_body = (
                f"# {clean_title}\n\n"
                f"{opening_sentence}\n\n"
                f"{message_val if message_val else 'Cuando analizas la situación con perspectiva, la clave no está en acumular conceptos teóricos, sino en observar qué ocurre cuando llevamos estas ideas al terreno práctico.'}"
                f"{ans_section}\n\n"
                f"## {sec1_title}\n\n"
                f"Existe una trampa habitual al pensar en esto: asumir que necesitamos tener todo resuelto antes de dar el primer paso. "
                f"En la práctica, al abordar '{sec1_title.lower()}', descubres que la claridad no precede a la acción, sino que surge directamente de ella.\n\n"
                f"## {sec2_title}\n\n"
                f"Al poner a prueba estas ideas, la teoría choca con la realidad. Lo más valioso de '{sec2_title.lower()}' "
                f"es que los descubrimientos principales casi nunca ocurren durante la planificación inicial, sino durante la ejecución directa.\n\n"
                f"## {sec3_title}\n\n"
                f"Al final, lo importante no es aferrarte a una postura rígida, sino mantener el criterio para aprender y ajustar sobre la marcha. "
                f"Sacar estos pensamientos de la cabeza es el primer paso para construir algo que realmente valga la pena."
            )

            return json.dumps({
                "format": "article",
                "title": title_val,
                "content": article_body
            }, ensure_ascii=False)

        return json.dumps(DEFAULT_ARTICLE_RESPONSE, ensure_ascii=False)

