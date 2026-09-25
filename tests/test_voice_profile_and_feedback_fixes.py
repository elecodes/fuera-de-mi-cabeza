import asyncio
import json

import pytest

from app.llm.providers.mock import MockLLMClient
from app.memory.editorial_memory import EditorialMemory
from app.services.argument_griller import ArgumentGriller
from app.services.idea_explorer import IdeaExplorer
from app.services.voice_auditor import VoiceAuditor
from app.services.voice_editor import VoiceEditor
from app.services.voice_profile import load_voice_profile


def test_load_voice_profile_combines_guide_samples_and_memory(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "voice_guide.md").write_text("GUIA", encoding="utf-8")
    (data_dir / "voice_samples.md").write_text("MUESTRAS", encoding="utf-8")

    memory_file = tmp_path / "memory.json"
    memory = EditorialMemory(memory_file=memory_file)
    memory.add_preference("style_rules", "Frases cortas")

    context = load_voice_profile(memory, base_dir=tmp_path)

    assert "GUIA" in context
    assert "MUESTRAS" in context
    assert "Frases cortas" in context


def test_load_voice_profile_ignores_placeholder_samples(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "voice_guide.md").write_text("GUIA", encoding="utf-8")
    (data_dir / "voice_samples.md").write_text("[Pega aquí tus textos]", encoding="utf-8")

    context = load_voice_profile(EditorialMemory(memory_file=tmp_path / "m.json"), base_dir=tmp_path)

    assert "Pega aquí" not in context


def test_load_voice_profile_falls_back_to_editorial_profile_without_guide(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    profile_file = data_dir / "editorial_profile.md"
    profile_file.write_text("PERFIL ANTIGUO", encoding="utf-8")

    context = load_voice_profile(
        EditorialMemory(memory_file=tmp_path / "m.json"),
        profile_path=profile_file,
        base_dir=tmp_path,
    )

    assert "PERFIL ANTIGUO" in context


@pytest.mark.parametrize("service_cls", [VoiceAuditor, ArgumentGriller, IdeaExplorer])
def test_services_accept_shared_editorial_memory(tmp_path, service_cls):
    # Antes de este cambio, VoiceAuditor/ArgumentGriller/IdeaExplorer solo leían
    # editorial_profile.md y no veían las reglas aprendidas en editorial_memory.json.
    memory = EditorialMemory(memory_file=tmp_path / "m.json")
    service = service_cls(llm_client=MockLLMClient(default_response="{}"), editorial_memory=memory)
    assert service.editorial_memory is memory


def test_editorial_memory_dedups_near_identical_rules(tmp_path):
    memory = EditorialMemory(memory_file=tmp_path / "m.json")
    memory.add_preference("style_rules", "Evitar enumeraciones de tres ítems que suenen forzadas")
    memory.add_preference(
        "style_rules",
        "Evita enumeraciones de tres ítems consecutivos que suenen forzadas",
    )

    rules = memory.get_all_memory()["style_rules"]
    assert len(rules) == 1


def test_editorial_memory_keeps_genuinely_different_rules(tmp_path):
    memory = EditorialMemory(memory_file=tmp_path / "m.json")
    memory.add_preference("style_rules", "Evitar enumeraciones de tres ítems forzadas")
    memory.add_preference("style_rules", "No usar comillas angulares")

    rules = memory.get_all_memory()["style_rules"]
    assert len(rules) == 2


def test_save_preference_raises_instead_of_storing_raw_feedback(tmp_path):
    async def _run():
        # El LLM devuelve algo que no es JSON válido: la síntesis falla.
        mock_llm = MockLLMClient(default_response="esto no es json")
        memory_file = tmp_path / "memory.json"
        profile_file = tmp_path / "editorial_profile.md"
        profile_file.write_text("# Perfil\n", encoding="utf-8")

        memory = EditorialMemory(memory_file=memory_file)
        editor = VoiceEditor(llm_client=mock_llm, editorial_memory=memory, profile_path=profile_file)

        with pytest.raises(RuntimeError):
            await editor.save_preference_to_profile(
                "esto no suena a mí, es demasiado formal y quiero que hable en primera persona"
            )

        # Nada de lo anterior debe haber quedado guardado como regla.
        all_rules = memory.get_all_memory()
        assert all(
            "no suena a mí" not in " ".join(v).lower() for v in all_rules.values()
        )

    asyncio.run(_run())


def test_save_preference_appends_rule_without_overwriting_profile(tmp_path):
    async def _run():
        mock_llm = MockLLMClient(
            default_response=json.dumps({"synthesized_rule": "Cerrar con una afirmación, no una pregunta."})
        )
        profile_file = tmp_path / "editorial_profile.md"
        profile_file.write_text("# Perfil Editorial Inicial\n", encoding="utf-8")

        memory = EditorialMemory(memory_file=tmp_path / "memory.json")
        editor = VoiceEditor(llm_client=mock_llm, editorial_memory=memory, profile_path=profile_file)

        rule = await editor.save_preference_to_profile("no me gusta cerrar con preguntas")

        assert rule == "Cerrar con una afirmación, no una pregunta."
        content = profile_file.read_text(encoding="utf-8")
        # El contenido original se conserva; solo se añade la nueva regla al final.
        assert content.startswith("# Perfil Editorial Inicial\n")
        assert "Cerrar con una afirmación" in content

    asyncio.run(_run())
