import asyncio
from app.llm.providers.mock import MockLLMClient
from app.models.draft import Draft
from app.services.voice_editor import VoiceEditor


def test_voice_editor_revise():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Este es el borrador inicial. [Nota: Añadir anécdota sobre mi primer trabajo].",
        )

        # Ya no se pide JSON: el LLM devuelve directamente el texto revisado en plano.
        mock_revised_response = (
            "Este es el borrador revisado integrando la anécdota de mi primer trabajo en una empresa pequeña."
        )

        mock_llm = MockLLMClient(default_response=mock_revised_response)
        editor = VoiceEditor(llm_client=mock_llm)

        revised = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="Mantené el tono conversational y desarrollá la nota sobre el primer trabajo",
        )

        # El formato y el título se conservan del borrador original: la revisión
        # nunca los reescribe por su cuenta, solo el contenido.
        assert revised.format == "article"
        assert revised.title == "Mi carrera como dev"
        assert "anécdota" in revised.content

    asyncio.run(_run())


def test_voice_editor_revise_ignores_title_even_if_model_tries_to_change_it():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Borrador inicial.",
        )

        # Si el modelo, pese a la instrucción, intenta colar un título nuevo dentro
        # del texto plano, no debe sustituir el título real del borrador.
        mock_llm = MockLLMClient(default_response="===TITULO===\nUn título inventado\n===CONTENIDO===\nTexto revisado.")
        editor = VoiceEditor(llm_client=mock_llm)

        revised = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="ajusta el tono",
        )

        assert revised.title == "Mi carrera como dev"

    asyncio.run(_run())

def test_voice_editor_multiple_revisions():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Este es el borrador inicial.",
        )

        mock_llm = MockLLMClient()
        editor = VoiceEditor(llm_client=mock_llm)

        # Primera revisión
        revised_1 = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="Hacerlo más cercano",
        )
        assert "Revisión Aplicada" not in revised_1.content

        # Segunda revisión recibiendo el borrador resultante de la primera
        revised_2 = await editor.revise(
            original_idea="Idea inicial",
            current_draft=revised_1,
            feedback_text="cambia el segundo párrafo para hacerlo más directo",
        )
        assert revised_2.content != revised_1.content
        assert "Revisión Aplicada" not in revised_2.content

def test_voice_editor_paragraph_rewrite_inplace():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Primer párrafo del post.\n\nSegundo párrafo que requiere cambio.\n\nTercer párrafo de cierre.",
        )

        mock_llm = MockLLMClient()
        editor = VoiceEditor(llm_client=mock_llm)

        revised = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="cambia el segundo párrafo para enfatizar el aprendizaje práctico",
        )

        assert "## Revisión Aplicada" not in revised.content
        assert "Segundo párrafo que requiere cambio." not in revised.content or "reescrito" in revised.content

def test_voice_editor_split_post():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Este es un post largo sobre desarrollo.\n\nPoblado con reflexiones y lecciones aprendidas.",
        )

        mock_llm = MockLLMClient()
        editor = VoiceEditor(llm_client=mock_llm)

        revised = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="divide el post en 2 para 2 posts, es muy largo",
        )

        assert "Parte 1" in revised.content
        assert "Parte 2" in revised.content

def test_voice_editor_note_stripping():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Esta es la frase original. [Nota: cambiar esta frase por algo más directo]. El resto sigue igual.",
        )

        mock_llm = MockLLMClient()
        editor = VoiceEditor(llm_client=mock_llm)

        revised = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="cambia la frase que se indica en la nota",
        )

        assert "[Nota:" not in revised.content
        assert "]" not in revised.content or "##" in revised.content

def test_voice_editor_intent_detection():
    assert VoiceEditor._detect_intent("Texto normal", "divide el post en 2") == "SPLIT_POST"
    assert VoiceEditor._detect_intent("Texto normal", "cambia el segundo párrafo") == "REWRITE_PARAGRAPH"
    assert VoiceEditor._detect_intent("Texto con [Nota: cambiar]", "revisa las notas") == "INTEGRATE_NOTES"
    assert VoiceEditor._detect_intent("Texto normal", "hacerlo más ameno") == "GENERAL_REVISION"





