import asyncio
import json
from app.llm.providers.mock import MockLLMClient
from app.models.analysis import IdeaAnalysis
from app.services.content_planner import ContentPlanner


def test_content_planner_plan():
    async def _run():
        mock_analysis = IdeaAnalysis(
            core_idea="Reflexión sobre el trabajo dev",
            possible_angles=["Ángulo 1"],
            potential_audience="Developers",
            emotional_tone="Reflexivo",
            recommended_format="article",
            questions=["Q1"],
        )

        mock_plan_json = {
            "format": "article",
            "title_options": ["Título 1", "Título 2"],
            "central_message": "Programar es solo una herramienta para construir cosas reales.",
            "opening_direction": "Iniciar con una duda sobre el rol de dev.",
            "key_points": ["Punto 1", "Punto 2", "Punto 3"],
            "ending_direction": "Cierre sutil sin moraleja.",
        }

        mock_llm = MockLLMClient(default_response=json.dumps(mock_plan_json))
        planner = ContentPlanner(llm_client=mock_llm)

        plan = await planner.plan(
            original_idea="No sé si quiero seguir siendo dev",
            analysis=mock_analysis,
            user_answers=["Me aburre la rutina"],
        )

        assert plan.format == "article"
        assert len(plan.title_options) == 2
        assert "Programar es solo una herramienta" in plan.central_message
        assert len(plan.key_points) == 3

    asyncio.run(_run())
