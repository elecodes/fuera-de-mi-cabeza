"""
Helpers para leer la salida del LLM cuando se le pide texto plano en vez de JSON.

Antes, generate_note/generate_article/revise pedían al modelo que devolviera
el borrador entero envuelto en un objeto JSON (con el contenido como un único
string escapado). Eso obligaba al modelo a escribir con un ojo puesto en el
formato en vez de en la prosa, y cualquier comilla o salto de línea mal escapado
rompía el parseo. Ahora se le pide el texto en plano, con marcadores simples
solo cuando de verdad hace falta separar dos campos (el título de un artículo).
"""

import re

TITLE_MARKER = "===TITULO==="
CONTENT_MARKER = "===CONTENIDO==="

_FENCE_RE = re.compile(r"^```[a-zA-Z]*\n(.*)\n```$", re.DOTALL)


def strip_code_fences(text: str) -> str:
    """
    Quita un bloque de código envolvente (```...```) si el modelo, pese a que
    se le pidió texto plano, envuelve la respuesta en una valla de Markdown.
    """
    text = text.strip()
    match = _FENCE_RE.match(text)
    if match:
        return match.group(1).strip()
    return text


def parse_titled_content(
    raw_response: str,
    title_marker: str = TITLE_MARKER,
    content_marker: str = CONTENT_MARKER,
) -> tuple[str | None, str]:
    """
    Separa un título opcional del contenido a partir de los marcadores
    ===TITULO=== / ===CONTENIDO===. Si el modelo no incluye el marcador de
    título (o de contenido), se trata todo el texto como contenido.
    """
    text = strip_code_fences(raw_response)

    if content_marker not in text:
        return None, text.strip()

    before_content, content = text.split(content_marker, 1)
    content = strip_code_fences(content)

    title: str | None = None
    if title_marker in before_content:
        title = before_content.split(title_marker, 1)[1].strip()
        title = title or None

    return title, content.strip()
