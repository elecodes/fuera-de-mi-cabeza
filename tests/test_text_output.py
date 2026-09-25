from app.services.text_output import parse_titled_content, strip_code_fences


def test_strip_code_fences_removes_wrapping_fence():
    text = "```markdown\nHola mundo\n```"
    assert strip_code_fences(text) == "Hola mundo"


def test_strip_code_fences_leaves_plain_text_untouched():
    text = "Hola mundo, sin vallas."
    assert strip_code_fences(text) == text


def test_parse_titled_content_splits_title_and_content():
    raw = "===TITULO===\nMi título\n===CONTENIDO===\nPrimera línea.\n\nSegunda línea."
    title, content = parse_titled_content(raw)
    assert title == "Mi título"
    assert content == "Primera línea.\n\nSegunda línea."


def test_parse_titled_content_without_title_marker_returns_none_title():
    raw = "===CONTENIDO===\nSolo contenido, sin título."
    title, content = parse_titled_content(raw)
    assert title is None
    assert content == "Solo contenido, sin título."


def test_parse_titled_content_without_any_marker_treats_everything_as_content():
    raw = "El modelo ignoró los marcadores y devolvió solo prosa."
    title, content = parse_titled_content(raw)
    assert title is None
    assert content == raw


def test_parse_titled_content_strips_wrapping_code_fence():
    raw = "```\n===TITULO===\nTítulo\n===CONTENIDO===\nContenido en una valla.\n```"
    title, content = parse_titled_content(raw)
    assert title == "Título"
    assert content == "Contenido en una valla."
