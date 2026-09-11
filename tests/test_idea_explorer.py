import asyncio
import json
from app.llm.providers.mock import MockLLMClient
from app.services.idea_explorer import IdeaExplorer


def test_idea_explorer_analyze_valid():
    async def _run():
        mock_json = {
            "core_idea": "Evaluar el rumbo profesional en programación",
            "possible_angles": [
                "El paso de escribir código a diseñar productos",
                "Burnout vs falta de propósito",
            ],
            "potential_audience": "Developers y profesionales de tecnología",
            "emotional_tone": "Reflexivo, honesto",
            "recommended_format": "both",
            "questions": [
                "¿Hace cuánto sentís este cansancio o duda?",
                "¿Hay algún proyecto reciente que te haya entusiasmado?",
            ],
        }

        mock_llm = MockLLMClient(default_response=f"```json\n{json.dumps(mock_json)}\n```")
        explorer = IdeaExplorer(llm_client=mock_llm)

        analysis = await explorer.analyze("No sé si quiero seguir trabajando como developer")

        assert analysis.core_idea == "Evaluar el rumbo profesional en programación"
        assert len(analysis.possible_angles) == 2
        assert analysis.recommended_format == "both"
        assert len(analysis.questions) == 2
        assert "Hace cuánto sentís" in analysis.questions[0]

    asyncio.run(_run())


def test_idea_explorer_trims_questions_over_max():
    async def _run():
        mock_json = {
            "core_idea": "Test",
            "possible_angles": ["Angle 1"],
            "potential_audience": "Audience",
            "emotional_tone": "Tone",
            "recommended_format": "note",
            "questions": ["Q1", "Q2", "Q3", "Q4", "Q5"],
        }

        mock_llm = MockLLMClient(default_response=json.dumps(mock_json))
        explorer = IdeaExplorer(llm_client=mock_llm)

        analysis = await explorer.analyze("Una idea cualquiera")

        assert len(analysis.questions) == 3
        assert analysis.questions == ["Q1", "Q2", "Q3"]

    asyncio.run(_run())
