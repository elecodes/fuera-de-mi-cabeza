import asyncio
import json
from app.llm.providers.mock import MockLLMClient
from app.models.content_plan import ContentPlan
from app.services.draft_generator import DraftGenerator


def test_draft_generator_note_and_article():
    async def _run():
        plan = ContentPlan(
            format="article",
            title_options=["Título A"],
            central_message="Mensaje central de prueba",
            opening_direction="Apertura",
            key_points=["Punto 1", "Punto 2"],
            ending_direction="Cierre",
        )

        mock_note_json = {
            "format": "note",
            "title": None,
            "content": "Esta es una note breve sobre la experiencia de construir.",
        }

        mock_llm_note = MockLLMClient(default_response=json.dumps(mock_note_json))
        generator = DraftGenerator(llm_client=mock_llm_note)

        note = await generator.generate_note(
            original_idea="Idea note",
            content_plan=plan,
            user_answers=[],
        )
        assert note.format == "note"
        assert "note breve" in note.content

        mock_article_json = {
            "format": "article",
            "title": "Título A",
            "content": "## Introducción\nContenido del artículo...",
        }

        mock_llm_article = MockLLMClient(default_response=json.dumps(mock_article_json))
        generator_art = DraftGenerator(llm_client=mock_llm_article)

        article = await generator_art.generate_article(
            original_idea="Idea artículo",
            content_plan=plan,
            user_answers=["Respuesta 1"],
            chosen_title="Título A",
        )
        assert article.format == "article"
        assert article.title == "Título A"
        assert "Contenido del artículo" in article.content

    asyncio.run(_run())
