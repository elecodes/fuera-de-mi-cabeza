import asyncio
import json
from app.services.profile_generator import ProfileGenerator
from app.llm.providers.mock import MockLLMClient


def test_profile_generator_extract_tone(tmp_path):
    async def _run():
        profile_json = {
            "opening_patterns": ["Entrada desde situaciones reales"],
            "preferred_connectors": ["pero", "de hecho"],
            "avoided_patterns": ["crucial", "optimizar"],
            "humor_and_tone": "Reflexivo y directo",
            "cadence_and_rhythm": "Combinación de oraciones cortas y largas",
            "generated_profile_markdown": "# Perfil Editorial Extraído\n\n## Tono\nReflexivo y directo.\n",
        }
        mock_llm = MockLLMClient(default_response=json.dumps(profile_json))
        target_profile_file = tmp_path / "editorial_profile.md"
        generator = ProfileGenerator(llm_client=mock_llm, profile_path=target_profile_file)

        samples = [
            "Muestra 1: El otro día me di cuenta de que programar sin pensar la arquitectura previa siempre trae problemas.",
            "Muestra 2: Lo bueno de simplificar las herramientas es que no te perdés en configuraciones absurdas.",
            "Muestra 3: El matiz está en entender qué resuelve cada herramienta antes de sumarla al stack.",
        ]

        res_content = await generator.update_editorial_profile(samples)

        assert "# Perfil Editorial Extraído" in res_content
        assert target_profile_file.exists()
        assert target_profile_file.read_text(encoding="utf-8") == res_content

    asyncio.run(_run())
