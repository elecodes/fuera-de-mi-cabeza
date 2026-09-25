import json
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.llm.providers.mock import MockLLMClient
from app.services.argument_griller import ArgumentGriller

client = TestClient(app)


def test_argument_griller_service():
    async def _run():
        mock_json = {
            "grill_questions": [
                "¿Qué diría un escéptico de tu postura?",
                "¿En qué vivencia concreta lo comprobaste?",
                "¿Para quién NO aplica esta reflexión?"
            ]
        }
        mock_llm = MockLLMClient(default_response=json.dumps(mock_json))
        griller = ArgumentGriller(llm_client=mock_llm)

        questions = await griller.generate_grill_questions(
            idea="Pensar con IA",
            arc_title="Del problema al aprendizaje",
            thought_sequence=["1. Duda", "2. Descubrimiento"]
        )

        assert len(questions) == 3
        assert "¿Qué diría un escéptico de tu postura?" in questions[0]

    import asyncio
    asyncio.run(_run())


def test_argument_griller_raises_on_invalid_json_instead_of_silent_fallback():
    async def _run():
        # Antes, una respuesta que no era JSON válido se disfrazaba de éxito
        # devolviendo 3 preguntas genéricas de repuesto sin que nadie se enterara.
        mock_llm = MockLLMClient(default_response="esto no es json")
        griller = ArgumentGriller(llm_client=mock_llm)

        with pytest.raises(RuntimeError):
            await griller.generate_grill_questions(
                idea="Pensar con IA",
                arc_title="Del problema al aprendizaje",
                thought_sequence=["1. Duda"],
            )

    import asyncio
    asyncio.run(_run())


def test_grill_mode_api_endpoints():
    # 1. Crear sesión
    res_init = client.post("/api/ideas", json={
        "idea": "Idea para probar el modo Grill",
        "raw_thoughts": ["Pensamiento 1", "Pensamiento 2"]
    })
    assert res_init.status_code == 200
    session_id = res_init.json()["id"]

    mock_analysis_json = {
        "core_idea": "Uso del modo grill",
        "connected_thoughts": ["Pensamiento 1", "Pensamiento 2"],
        "narrative_arcs": [
            {
                "id": "arc-1",
                "title": "Arco de prueba",
                "thought_sequence": ["1. Punto A", "2. Punto B"],
                "rationale": "Justificación de prueba"
            }
        ],
        "possible_angles": ["Ángulo 1"],
        "potential_audience": "Desarrolladores",
        "emotional_tone": "Reflexivo",
        "recommended_format": "article",
        "questions": ["¿Pregunta socrática?"]
    }

    mock_grill_json = {
        "grill_questions": [
            "1. Contra-argumento principal",
            "2. Evidencia personal",
            "3. Límite de la idea"
        ]
    }

    # Explore & Select Arc
    with patch("app.main.get_llm_client", return_value=MockLLMClient(default_response=json.dumps(mock_analysis_json))):
        client.post(f"/api/ideas/{session_id}/explore")

    res_arc = client.post(f"/api/ideas/{session_id}/select-arc", json={"arc_id": "arc-1"})
    assert res_arc.status_code == 200

    # Activar Modo Grill
    mock_grill_llm = MockLLMClient(default_response=json.dumps(mock_grill_json))
    with patch("app.main.get_llm_client", return_value=mock_grill_llm):
        res_grill = client.post(f"/api/ideas/{session_id}/grill")
        assert res_grill.status_code == 200
        session_data = res_grill.json()
        assert session_data["grill_mode"] is True
        assert len(session_data["grill_questions"]) == 3

    # Enviar Respuestas Grill
    res_answers = client.post(f"/api/ideas/{session_id}/grill/answers", json={
        "answers": ["1. Mi escéptico diría X", "2. Lo viví en proyecto Y", "3. No aplica si Z"]
    })
    assert res_answers.status_code == 200
    assert len(res_answers.json()["grill_answers"]) == 3
