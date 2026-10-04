# Perfil Editorial — Fuera de mi cabeza

Este archivo ya no se usa para generar borradores: `app/services/voice_profile.py`
construye el contexto de voz a partir de `data/voice_guide.md`, `data/voice_samples.md`
y `data/editorial_memory.json`.

Este archivo se conserva como registro legible de las reglas aprendidas por feedback
(ver `data/editorial_memory.json` para la versión que realmente usan los prompts).

## Reglas aprendidas
- Evitar adjetivos y verbos inflados (crucial, esencial, clave, optimizar, potenciar).
- No usar comillas angulares (« »).
- Usar femenino cuando la autora habla de sí misma (yo misma, no yo mismo).
- No inventar ejemplos, datos ni demostraciones que no existan.
- Hablar en primera persona, desde la experiencia propia.
- Evitar finalizar los textos con preguntas retóricas.
- Integrar las notas y modificaciones directamente en el borrador, sin crear versiones separadas.
- Evitar metáforas cliché y cierres genéricos; usar vocabulario preciso en español.
- Describir acciones concretas en vez de frases vagas.
- Mantener un tono íntimo y cercano, como si hablara directamente al lector.
- No emplear construcciones antitéticas tipo 'no es X, sino Y'.
- Sonar coloquial, natural y cercano, como una conversación real, sin formalidades excesivas.
- Español peninsular (tú, tienes, has probado), sin voseo.
- Evitar enumeraciones de tres ítems forzadas; reformular la idea o separar los elementos.
- Párrafos breves, claros y cercanos, sin repeticiones ni construcciones confusas.

## Expresiones prohibidas
- "No se trata de X, sino de Y"
- "una lista de comprobación: evita perder el hilo"
- "mapa interno"

## Nota sobre esta limpieza (2026-10-01)
Varias entradas de feedback reciente sobre tono, antítesis y tríos se habían
guardado por error como "expresiones favoritas" (es decir, como frases a usar
literalmente) en vez de como reglas de estilo — un bug de categorización ya
corregido (ver ADR 0023). Esta versión consolida esas entradas duplicadas en
las reglas de arriba, en la categoría correcta.
