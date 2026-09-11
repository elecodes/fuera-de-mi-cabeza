import asyncio
import json
from app.llm.providers.mock import MockLLMClient
from app.models.draft import Draft
from app.services.voice_editor import VoiceEditor


def test_voice_editor_revise():
    async def _run():
        initial_draft = Draft(
            format="article",
            title="Mi carrera como dev",
            content="Este es el borrador inicial demasiado formal.",
        )

        mock_revised_json = {
            "format": "article",
            "title": "Mi carrera como dev",
            "content": "Este es el borrador revisado más natural e individual.",
        }

        mock_llm = MockLLMClient(default_response=json.dumps(mock_revised_json))
        editor = VoiceEditor(llm_client=mock_llm)

        revised = await editor.revise(
            original_idea="Idea inicial",
            current_draft=initial_draft,
            feedback_text="Demasiado formal, prefiero algo más cercano",
        )

        assert revised.format == "article"
        assert revised.title == "Mi carrera como dev"
        assert "más natural" in revised.content

    asyncio.run(_run())
