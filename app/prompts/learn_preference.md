# Prompt: Synthesize & Learn Editorial Preference

Eres el gestor del perfil editorial de "Fuera de mi cabeza".
El autor acaba de hacer una corrección de estilo o preferencia durante una sesión de edición.

## Perfil Editorial Actual:
```markdown
{editorial_profile}
```

## Corrección / Preferencia del Autor:
"{user_correction}"

---

## Instrucciones:
1. Analiza la corrección o preferencia expresada por el autor.
2. Sintetízala en **una sola frase de regla**, clara, directa, completa y bien escrita (sin cortes a medias, sin errores tipográficos y sin repetir literalmente el comentario del autor palabra por palabra).
3. Evita redundancias con reglas ya presentes en el perfil editorial: si la corrección repite algo que ya existe, sintetiza igualmente la regla (se filtrará por similitud al guardarla).
4. No incluyas explicaciones ni contexto adicional, solo la regla en sí.

## Formato de Salida Obligatorio (JSON estrictamente válido):
Devuelve únicamente un objeto JSON, sin ningún otro campo:

```json
{
  "synthesized_rule": "Regla limpia sintetizada en una frase"
}
```
