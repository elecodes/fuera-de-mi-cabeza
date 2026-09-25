import asyncio
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

        # Ya no se pide JSON: el LLM devuelve texto plano para la Note...
        mock_note_response = "Esta es una note breve sobre la experiencia de construir."

        mock_llm_note = MockLLMClient(default_response=mock_note_response)
        generator = DraftGenerator(llm_client=mock_llm_note)

        note = await generator.generate_note(
            original_idea="Idea note",
            content_plan=plan,
            user_answers=[],
        )
        assert note.format == "note"
        assert note.title is None
        assert "note breve" in note.content

        # ...y título + contenido separados por marcadores para el Artículo.
        mock_article_response = (
            "===TITULO===\n"
            "Título A\n"
            "===CONTENIDO===\n"
            "## Introducción\nContenido del artículo..."
        )

        mock_llm_article = MockLLMClient(default_response=mock_article_response)
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
        assert "===TITULO===" not in article.content
        assert "===CONTENIDO===" not in article.content

    asyncio.run(_run())


def test_draft_generator_article_falls_back_to_chosen_title_without_markers():
    async def _run():
        plan = ContentPlan(
            format="article",
            title_options=["Título A"],
            central_message="Mensaje",
            opening_direction="Apertura",
            key_points=["Punto 1"],
            ending_direction="Cierre",
        )

        # Si el modelo no usa los marcadores (p. ej. un proveedor menos obediente),
        # todo el texto se trata como contenido y se conserva el título elegido.
        mock_llm = MockLLMClient(default_response="Contenido del artículo sin marcadores.")
        generator = DraftGenerator(llm_client=mock_llm)

        article = await generator.generate_article(
            original_idea="Idea artículo",
            content_plan=plan,
            user_answers=[],
            chosen_title="Título elegido",
        )
        assert article.title == "Título elegido"
        assert "Contenido del artículo sin marcadores." in article.content

    asyncio.run(_run())
