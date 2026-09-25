import asyncio
import json
from app.services.voice_editor import VoiceEditor
from app.llm.providers.mock import MockLLMClient


def test_voice_editor_continuous_learning(tmp_path):
    async def _run():
        learn_response = {
            "synthesized_rule": "Evitar finalizar textos con preguntas retóricas.",
        }
        mock_llm = MockLLMClient(default_response=json.dumps(learn_response))

        profile_file = tmp_path / "editorial_profile.md"
        profile_file.write_text("# Perfil Editorial Inicial\n", encoding="utf-8")

        editor = VoiceEditor(llm_client=mock_llm, profile_path=profile_file)

        synthesized_rule = await editor.save_preference_to_profile(
            "No me gusta cómo queda cerrar con preguntas al lector, preferiría cierres secos con una afirmación."
        )

        # La regla sintetizada es lo que se guarda y se devuelve, no el borrador
        # de perfil completo: el archivo original se conserva y solo se le
        # añade la nueva regla, en vez de sobrescribirlo con todo el contexto.
        assert synthesized_rule == "Evitar finalizar textos con preguntas retóricas."
        profile_content = profile_file.read_text(encoding="utf-8")
        assert profile_content.startswith("# Perfil Editorial Inicial\n")
        assert "Evitar finalizar textos con preguntas retóricas." in profile_content

    asyncio.run(_run())
