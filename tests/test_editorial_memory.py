import asyncio
import json
from app.memory.editorial_memory import EditorialMemory
from app.services.draft_generator import DraftGenerator
from app.services.voice_editor import VoiceEditor
from app.llm.providers.mock import MockLLMClient


def test_editorial_memory_crud(tmp_path):
    memory_file = tmp_path / "test_memory.json"
    memory = EditorialMemory(memory_file=memory_file)

    # Inicialización por defecto
    all_data = memory.get_all_memory()
    assert "favorite_expressions" in all_data
    assert "forbidden_words" in all_data
    assert "style_rules" in all_data

    # Agregar preferencias
    memory.add_preference("favorite_expressions", "el caso es que")
    memory.add_preference("forbidden_words", "crucial")
    memory.add_preference("style_rules", "frases cortas al inicio")

    all_data = memory.get_all_memory()
    assert "el caso es que" in all_data["favorite_expressions"]
    assert "crucial" in all_data["forbidden_words"]
    assert "frases cortas al inicio" in all_data["style_rules"]

    # Formateo de contexto para prompts
    context_str = memory.get_context()
    assert "Memoria de Voz y Estilo Personal del Autor" in context_str
    assert "el caso es que" in context_str
    assert "crucial" in context_str

    # Eliminar preferencia
    removed = memory.delete_preference("forbidden_words", "crucial")
    assert removed is True
    assert "crucial" not in memory.get_all_memory()["forbidden_words"]


def test_draft_generator_injects_memory(tmp_path):
    async def _run():
        memory_file = tmp_path / "test_memory.json"
        memory = EditorialMemory(memory_file=memory_file)
        memory.add_preference("favorite_expressions", "en la práctica")

        mock_llm = MockLLMClient(default_response=json.dumps({"format": "note", "title": None, "content": "Test note"}))
        generator = DraftGenerator(llm_client=mock_llm, editorial_memory=memory)

        loaded_profile = generator._load_profile()
        assert "en la práctica" in loaded_profile

    asyncio.run(_run())


def test_voice_editor_learning_updates_memory(tmp_path):
    async def _run():
        memory_file = tmp_path / "test_memory.json"
        profile_file = tmp_path / "test_profile.md"
        profile_file.write_text("# Perfil Editorial Inicial\n", encoding="utf-8")

        memory = EditorialMemory(memory_file=memory_file)
        mock_llm = MockLLMClient(
            default_response=json.dumps({
                "synthesized_rule": "Usar preferentemente la expresión 'el caso es que'",
                "updated_profile_markdown": "# Perfil Editorial\n\n- **Regla**: Usar 'el caso es que'",
            })
        )

        editor = VoiceEditor(llm_client=mock_llm, editorial_memory=memory, profile_path=profile_file)
        await editor.save_preference_to_profile("Prefiero usar la expresión 'el caso es que' en mis artículos")

        all_data = memory.get_all_memory()
        assert len(all_data["favorite_expressions"]) > 0

    asyncio.run(_run())
