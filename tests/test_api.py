import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.llm.providers.mock import MockLLMClient

client = TestClient(app)


def test_full_api_flow():
    # 1. Crear sesión con brain dump / thoughts sueltos
    res = client.post("/api/ideas", json={
        "idea": "- Idea 1: La IA ayuda a pensar\n- Idea 2: No sé si programar más",
        "raw_thoughts": ["La IA ayuda a pensar", "No sé si programar más"]
    })
    assert res.status_code == 200
    session_data = res.json()
    session_id = session_data["id"]

    # Mock respuestas LLM para cada fase
    mock_analysis_json = {
        "core_idea": "Uso de la IA en procesos de aprendizaje personal",
        "connected_thoughts": ["La IA ayuda a pensar", "Dudas sobre seguir programando"],
        "narrative_arcs": [
            {
                "id": "arc-1",
                "title": "Del dilema al aprendizaje",
                "thought_sequence": ["1. Reflexión sobre programar", "2. Descubrimiento de la IA"],
                "rationale": "Conecta la duda con la solución"
            }
        ],
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

    # Ya no se pide JSON al LLM para el draft: título y contenido van
    # separados por los marcadores ===TITULO=== / ===CONTENIDO===.
    mock_draft_response = (
        "===TITULO===\n"
        "IA para Aprender\n"
        "===CONTENIDO===\n"
        "Contenido del artículo sobre IA..."
    )

    mock_audit_json = {
        "score": 95,
        "passed": True,
        "cadence_analysis": "Variación correcta",
        "issues": []
    }

    # La revisión tampoco pide JSON: solo el contenido revisado en plano
    # (el título y el formato se conservan del borrador anterior).
    mock_revised_response = "Contenido del artículo revisado..."

    # 2. Explore
    mock_explore_llm = MockLLMClient(default_response=json.dumps(mock_analysis_json))
    with patch("app.main.get_llm_client", return_value=mock_explore_llm):
        res_exp = client.post(f"/api/ideas/{session_id}/explore")
        assert res_exp.status_code == 200
        assert res_exp.json()["analysis"]["core_idea"] == "Uso de la IA en procesos de aprendizaje personal"
        assert len(res_exp.json()["analysis"]["narrative_arcs"]) == 1

    # 3. Select Narrative Arc
    res_arc = client.post(f"/api/ideas/{session_id}/select-arc", json={"arc_id": "arc-1"})
    assert res_arc.status_code == 200
    assert res_arc.json()["selected_arc"]["id"] == "arc-1"

    # 4. Answers
    res_ans = client.post(f"/api/ideas/{session_id}/answers", json={"answers": ["Uso ChatGPT para resumir"]})
    assert res_ans.status_code == 200
    assert res_ans.json()["user_answers"] == ["Uso ChatGPT para resumir"]

    # 5. Plan
    mock_plan_llm = MockLLMClient(default_response=json.dumps(mock_plan_json))
    with patch("app.main.get_llm_client", return_value=mock_plan_llm):
        res_plan = client.post(f"/api/ideas/{session_id}/plan")
        assert res_plan.status_code == 200
        assert res_plan.json()["content_plan"]["central_message"] == "La IA amplifica el pensamiento."

    # 6. Draft
    mock_draft_llm = MockLLMClient(default_response=mock_draft_response)
    with patch("app.main.get_llm_client", return_value=mock_draft_llm):
        res_draft = client.post(f"/api/ideas/{session_id}/draft", json={"format": "article"})
        assert res_draft.status_code == 200
        assert res_draft.json()["draft"]["title"] == "IA para Aprender"
        assert res_draft.json()["draft"]["content"] == "Contenido del artículo sobre IA..."

    # 7. Audit
    mock_audit_llm = MockLLMClient(default_response=json.dumps(mock_audit_json))
    with patch("app.main.get_llm_client", return_value=mock_audit_llm):
        res_audit = client.post(f"/api/ideas/{session_id}/audit")
        assert res_audit.status_code == 200
        assert res_audit.json()["voice_audit"]["score"] == 95

    # 8. Memory preference
    res_mem = client.post("/api/memory/preference", json={"category": "style_rules", "preference": "Evitar palabras infladas"})
    assert res_mem.status_code == 200

    # 9. Revise
    mock_revise_llm = MockLLMClient(default_response=mock_revised_response)
    with patch("app.main.get_llm_client", return_value=mock_revise_llm):
        res_rev = client.post(f"/api/ideas/{session_id}/revise", json={"feedback": "Hacerlo más cercano"})
        assert res_rev.status_code == 200
        assert res_rev.json()["draft"]["content"] == "Contenido del artículo revisado..."
        assert res_rev.json()["feedback"] == ["Hacerlo más cercano"]

    # 10. Get Session
    res_get = client.get(f"/api/sessions/{session_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == session_id

    # 11. Export to Drive
    with patch("app.main.DriveUploader") as MockUploader:
        MockUploader.return_value.upload_draft_as_google_doc.return_value = "https://docs.google.com/document/d/xyz/edit"
        res_drive = client.post(f"/api/ideas/{session_id}/export-to-drive")
        assert res_drive.status_code == 200
        assert res_drive.json()["drive_url"] == "https://docs.google.com/document/d/xyz/edit"
        MockUploader.return_value.upload_draft_as_google_doc.assert_called_once_with(
            title="IA para Aprender",
            content_markdown="Contenido del artículo revisado...",
        )


def test_export_to_drive_without_draft_returns_400():
    res = client.post("/api/ideas", json={"idea": "Una idea sin borrador todavía"})
    session_id = res.json()["id"]

    res_drive = client.post(f"/api/ideas/{session_id}/export-to-drive")
    assert res_drive.status_code == 400


def test_export_to_drive_surfaces_real_error():
    res = client.post("/api/ideas", json={"idea": "Una idea de prueba"})
    session_id = res.json()["id"]

    mock_analysis_json = {
        "core_idea": "Idea de prueba",
        "connected_thoughts": ["Idea de prueba"],
        "narrative_arcs": [{
            "id": "arc-1", "title": "Arco", "thought_sequence": ["1. Paso"], "rationale": "R"
        }],
        "possible_angles": ["Ángulo 1"],
        "potential_audience": "Audiencia",
        "emotional_tone": "Neutral",
        "recommended_format": "note",
        "questions": ["¿Qué estabas haciendo justo antes?"]
    }
    with patch("app.main.get_llm_client", return_value=MockLLMClient(default_response=json.dumps(mock_analysis_json))):
        client.post(f"/api/ideas/{session_id}/explore")
        client.post(f"/api/ideas/{session_id}/select-arc", json={"arc_id": "arc-1"})

    mock_plan_json = {
        "format": "note",
        "title_options": ["Título"], "central_message": "Mensaje",
        "opening_direction": "Apertura", "key_points": ["Punto"], "ending_direction": "Cierre"
    }
    with patch("app.main.get_llm_client", return_value=MockLLMClient(default_response=json.dumps(mock_plan_json))):
        client.post(f"/api/ideas/{session_id}/plan")

    with patch("app.main.get_llm_client", return_value=MockLLMClient(default_response="Contenido de una nota.")):
        client.post(f"/api/ideas/{session_id}/draft", json={"format": "note"})

    # Si Drive falla (credenciales, permisos, lo que sea), el error real debe
    # verse en la respuesta, nunca un 200 silencioso ni un mock disfrazado.
    with patch("app.main.DriveUploader") as MockUploader:
        MockUploader.return_value.upload_draft_as_google_doc.side_effect = RuntimeError("GOOGLE_DRIVE_FOLDER_ID no está configurado.")
        res_drive = client.post(f"/api/ideas/{session_id}/export-to-drive")
        assert res_drive.status_code == 500
        assert "GOOGLE_DRIVE_FOLDER_ID" in res_drive.json()["detail"]


def test_architecture_endpoint():
    res = client.get("/architecture")
    assert res.status_code == 200
    assert "Archify Verified IR" in res.text


def test_architecture_sequence_endpoint():
    res = client.get("/architecture/sequence")
    assert res.status_code == 200
    assert "Archify Sequence IR" in res.text


def test_update_diagram_metadata_script():
    from scripts.update_diagram_metadata import main as update_meta
    update_meta()
    res = client.get("/architecture")
    assert "git:" in res.text



