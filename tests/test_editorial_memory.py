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


def test_voice_editor_learning_bans_expression_correctly(tmp_path):
    # Bug real: pedir que se DEJE de usar una expresión ("no uses esta
    # expresión...") se guardaba en "favorite_expressions" en vez de
    # "forbidden_words", porque "no usar" contiene literalmente "usar" —
    # invirtiendo el sentido exacto de lo pedido. La categoría se decide por
    # el feedback del autor (user_correction), no por la regla ya sintetizada,
    # así que la palabra "no uses" debe estar en el texto que se le pasa.
    async def _run():
        memory_file = tmp_path / "test_memory.json"
        profile_file = tmp_path / "test_profile.md"
        profile_file.write_text("# Perfil Editorial Inicial\n", encoding="utf-8")

        memory = EditorialMemory(memory_file=memory_file)
        mock_llm = MockLLMClient(
            default_response=json.dumps({
                "synthesized_rule": "No usar la expresión 'lista de comprobación: evita perder el hilo'.",
            })
        )

        editor = VoiceEditor(llm_client=mock_llm, editorial_memory=memory, profile_path=profile_file)
        await editor.save_preference_to_profile(
            "No uses esta expresión en cada nota: 'una lista de comprobación: evita perder el hilo'"
        )

        all_data = memory.get_all_memory()
        assert len(all_data["forbidden_words"]) > 0
        assert all_data["favorite_expressions"] == []

    asyncio.run(_run())


def test_voice_editor_learning_still_files_genuine_favorites_correctly(tmp_path):
    # Caso contrario: pedir que SÍ se use una expresión debe seguir yendo a
    # favorite_expressions, sin que el arreglo del bug de arriba lo rompa.
    async def _run():
        memory_file = tmp_path / "test_memory.json"
        profile_file = tmp_path / "test_profile.md"
        profile_file.write_text("# Perfil Editorial Inicial\n", encoding="utf-8")

        memory = EditorialMemory(memory_file=memory_file)
        mock_llm = MockLLMClient(
            default_response=json.dumps({"synthesized_rule": "Usar la muletilla 'la verdad es que' con naturalidad."})
        )

        editor = VoiceEditor(llm_client=mock_llm, editorial_memory=memory, profile_path=profile_file)
        await editor.save_preference_to_profile("Me gusta mucho la muletilla 'la verdad es que', úsala más")

        all_data = memory.get_all_memory()
        assert len(all_data["favorite_expressions"]) > 0
        assert all_data["forbidden_words"] == []

    asyncio.run(_run())
