import asyncio
import json
from app.services.voice_editor import VoiceEditor
from app.llm.providers.mock import MockLLMClient


def test_voice_editor_continuous_learning(tmp_path):
    async def _run():
        learn_response = {
            "synthesized_rule": "Evitar finalizar textos con preguntas retóricas.",
            "updated_profile_markdown": "# Perfil Editorial\n\n- **Regla**: Evitar preguntas retóricas al final.",
        }
        mock_llm = MockLLMClient(default_response=json.dumps(learn_response))

        profile_file = tmp_path / "editorial_profile.md"
        profile_file.write_text("# Perfil Editorial Inicial\n", encoding="utf-8")

        editor = VoiceEditor(llm_client=mock_llm, profile_path=profile_file)

        updated_profile = await editor.save_preference_to_profile(
            "No me gusta cómo queda cerrar con preguntas al lector, preferiría cierres secos con una afirmación."
        )

        assert "Evitar preguntas retóricas" in updated_profile
        assert profile_file.read_text(encoding="utf-8") == updated_profile

    asyncio.run(_run())
