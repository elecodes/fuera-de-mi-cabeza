import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.llm.providers.mock import MockLLMClient

client = TestClient(app)


def test_full_api_flow():
    # 1. Crear sesión
    res = client.post("/api/ideas", json={"idea": "Quiero hablar sobre cómo la IA ayuda a aprender"})
    assert res.status_code == 200
    session_data = res.json()
    session_id = session_data["id"]

    # Mock respuestas LLM para cada fase
    mock_analysis_json = {
        "core_idea": "Uso de la IA en procesos de aprendizaje personal",
        "possible_angles": ["La IA como tutor de conversación", "Aprender haciendo"],
        "potential_audience": "Educadores y estudiantes",
        "emotional_tone": "Entusiasta pero crítico",
        "recommended_format": "article",
        "questions": ["¿Qué usás para aprender hoy?"],
    }

    mock_plan_json = {
        "format": "article",
        "title_options": ["IA para Aprender"],
        "central_message": "La IA amplifica el pensamiento.",
        "opening_direction": "Abrir con una experiencia",
        "key_points": ["Punto 1", "Punto 2"],
        "ending_direction": "Cierre reflexivo",
    }

    mock_draft_json = {
        "format": "article",
        "title": "IA para Aprender",
        "content": "Contenido del artículo sobre IA...",
    }

    mock_revised_json = {
        "format": "article",
        "title": "IA para Aprender",
        "content": "Contenido del artículo revisado...",
    }

    # 2. Explore
    mock_explore_llm = MockLLMClient(default_response=json.dumps(mock_analysis_json))
    with patch("app.main.get_llm_client", return_value=mock_explore_llm):
        res_exp = client.post(f"/api/ideas/{session_id}/explore")
        assert res_exp.status_code == 200
        assert res_exp.json()["analysis"]["core_idea"] == "Uso de la IA en procesos de aprendizaje personal"

    # 3. Answers
    res_ans = client.post(f"/api/ideas/{session_id}/answers", json={"answers": ["Uso ChatGPT para resumir"]})
    assert res_ans.status_code == 200
    assert res_ans.json()["user_answers"] == ["Uso ChatGPT para resumir"]

    # 4. Plan
    mock_plan_llm = MockLLMClient(default_response=json.dumps(mock_plan_json))
    with patch("app.main.get_llm_client", return_value=mock_plan_llm):
        res_plan = client.post(f"/api/ideas/{session_id}/plan")
        assert res_plan.status_code == 200
        assert res_plan.json()["content_plan"]["central_message"] == "La IA amplifica el pensamiento."

    # 5. Draft
    mock_draft_llm = MockLLMClient(default_response=json.dumps(mock_draft_json))
    with patch("app.main.get_llm_client", return_value=mock_draft_llm):
        res_draft = client.post(f"/api/ideas/{session_id}/draft", json={"format": "article"})
        assert res_draft.status_code == 200
        assert res_draft.json()["draft"]["title"] == "IA para Aprender"

    # 6. Revise
    mock_revise_llm = MockLLMClient(default_response=json.dumps(mock_revised_json))
    with patch("app.main.get_llm_client", return_value=mock_revise_llm):
        res_rev = client.post(f"/api/ideas/{session_id}/revise", json={"feedback": "Hacerlo más cercano"})
        assert res_rev.status_code == 200
        assert res_rev.json()["draft"]["content"] == "Contenido del artículo revisado..."
        assert res_rev.json()["feedback"] == ["Hacerlo más cercano"]

    # 7. Get Session
    res_get = client.get(f"/api/sessions/{session_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == session_id
