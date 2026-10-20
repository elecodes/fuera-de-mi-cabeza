import pytest
from pathlib import Path
from unittest.mock import AsyncMock
from app.llm.client import LLMClient
from app.services.anatomy_generator import (
    AnatomyGenerator,
    parse_anatomy_response,
    slugify,
)


def test_slugify():
    assert slugify("Token Bucket: Rate Limiter!") == "token-bucket-rate-limiter"
    assert slugify("Árboles y Máquinas") == "arboles-y-maquinas"


def test_parse_anatomy_response_with_delimiters():
    raw_response = """
===TITULO===
Tolva Hidráulica de Tokens
===METAFORA===
Un embudo con válvula flotante y contrapeso de mercurio
===HTML===
<!DOCTYPE html>
<html>
<body><svg></svg></body>
</html>
"""
    title, metaphor, html = parse_anatomy_response(raw_response, default_concept="Tokens")
    assert title == "Tolva Hidráulica de Tokens"
    assert metaphor == "Un embudo con válvula flotante y contrapeso de mercurio"
    assert html == "<!DOCTYPE html>\n<html>\n<body><svg></svg></body>\n</html>"


def test_parse_anatomy_response_code_fence_cleanup():
    raw_response = """
===TITULO===
Máquina
===METAFORA===
Pistón
===HTML===
```html
<!DOCTYPE html>
<html><body>Piston</body></html>
```
"""
    title, metaphor, html = parse_anatomy_response(raw_response, default_concept="Piston")
    assert html == "<!DOCTYPE html>\n<html><body>Piston</body></html>"


def test_parse_anatomy_response_fallback():
    raw_response = "```html\n<div>Sin delimitadores</div>\n```"
    title, metaphor, html = parse_anatomy_response(raw_response, default_concept="Concepto X")
    assert title == "Concepto X"
    assert metaphor == "Mecanismo interactivo"
    assert html == "<div>Sin delimitadores</div>"


@pytest.mark.asyncio
async def test_anatomy_generator_flow(tmp_path: Path):
    mock_llm = AsyncMock(spec=LLMClient)
    mock_llm.generate.return_value = """
===TITULO===
El Péndulo de Concurrencia
===METAFORA===
Un conjunto de péndulos acoplados que sincronizan impulsos
===HTML===
<!DOCTYPE html>
<html>
<head><title>Pendulo</title></head>
<body><svg><circle cx="50" cy="50" r="10"/></svg></body>
</html>
"""

    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Concept: {concept}\nContext: {context}", encoding="utf-8")
    visuals_dir = tmp_path / "visuals"

    generator = AnatomyGenerator(
        llm_client=mock_llm,
        visuals_dir=visuals_dir,
        prompt_path=prompt_file,
    )

    asset = await generator.generate_visual(
        concept="Concurrencia asíncrona en Python",
        context="Capítulo sobre async/await",
    )

    assert asset.title == "El Péndulo de Concurrencia"
    assert asset.metaphor == "Un conjunto de péndulos acoplados que sincronizan impulsos"
    assert "el-pendulo-de-concurrencia-" in asset.slug
    assert "<svg>" in asset.html_content

    # Verificar que el archivo se guardó físicamente
    saved_file = visuals_dir / f"{asset.slug}.html"
    assert saved_file.exists()
    assert saved_file.read_text(encoding="utf-8") == asset.html_content

    # Verificar get_visual_html
    retrieved = generator.get_visual_html(asset.slug)
    assert retrieved == asset.html_content
    assert generator.get_visual_html("inexistente") is None

    # Verificar snippet de Substack
    snippet = asset.substack_snippet(base_url="https://fuerademicabeza.com")
    assert "https://fuerademicabeza.com/visuals/" in snippet
    assert asset.title in snippet
