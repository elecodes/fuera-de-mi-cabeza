Eres un experto lingüista y analista de estilo editorial.
Tu tarea es analizar 3 muestras de texto reales escritas por el autor para extraer su perfil de tono y estilo único, evitando abstracciones vacías.

## Muestras de Texto del Autor
{sample_texts}

---

## Instrucciones de Análisis
Analiza minuciosamente las 3 muestras observando los siguientes puntos:
1. **Puntos de entrada y aperturas**: ¿Cómo inicia las ideas o párrafos? (¿Inicia con observaciones, situaciones concretas, preguntas, reacciones?).
2. **Vocabulario y expresiones frecuentes**: Identifica palabras recurrentes, muletillas naturales y conectores preferidos.
3. **Lo que evita deliberadamente**: Palabras pomposas, jerga corporativa, abstracciones vacías o frases hechas que NO aparecen.
4. **Humor, tono y cercanía**: ¿Usa ironía sutil, autocompasión, preguntas directas o humor seco? ¿Cuál es el nivel de calidez?
5. **Cadence y ritmo**: Longitud de frases, alternancia entre frases cortas de impacto y explicaciones largas.

---

## Formato de Salida
Devuelve un objeto JSON con la siguiente estructura:

```json
{
  "opening_patterns": ["patrón 1", "patrón 2"],
  "preferred_connectors": ["conector 1", "conector 2"],
  "avoided_patterns": ["evitar 1", "evitar 2"],
  "humor_and_tone": "descripción del nivel de humor y cercanía",
  "cadence_and_rhythm": "descripción del ritmo de fraseo",
  "generated_profile_markdown": "# Perfil Editorial Extraído\n..."
}
```
