from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.llm.providers.mock import MockLLMClient

client = TestClient(app)


def test_visuals_api_flow():
    # 1. Crear sesión
    res = client.post("/api/ideas", json={
        "idea": "Explicación de cómo funciona un Rate Limiter con Token Bucket",
        "raw_thoughts": ["Token Bucket", "Rate Limiting"]
    })
    assert res.status_code == 200
    session_id = res.json()["id"]

    # 2. Asignar un borrador para tener contexto
    client.post(f"/api/ideas/{session_id}/draft/update", json={
        "title": "Domando el Tráfico con Token Bucket",
        "content": "Un rate limiter previene saturaciones permitiendo ráfagas controladas mediante tokens acumulados en un depósito."
    })

    # 3. Disparar generación de visual de Anatomy (sin especificar concepto: lo deduce del borrador)
    with patch("app.main.get_llm_client", return_value=MockLLMClient()):
        vis_res = client.post(f"/api/ideas/{session_id}/visuals", json={})
        assert vis_res.status_code == 200
        data = vis_res.json()
        assert data["visual_asset"] is not None
        slug = data["visual_asset"]["slug"]
        assert slug is not None
        assert "tolva" in data["visual_asset"]["title"].lower() or "isométrica" in data["visual_asset"]["title"].lower()

    # 4. Servir la página interactiva del companion en /visuals/{slug}
    html_res = client.get(f"/visuals/{slug}")
    assert html_res.status_code == 200
    assert "text/html" in html_res.headers["content-type"]
    assert "<!DOCTYPE html>" in html_res.text
    assert "Operar máquina" in html_res.text

    # 5. Obtener el snippet formateado para Substack
    snippet_res = client.get(f"/api/ideas/{session_id}/visuals/snippet")
    assert snippet_res.status_code == 200
    snippet_data = snippet_res.json()
    assert f"/visuals/{slug}" in snippet_data["snippet"]
    assert "Explorá la máquina interactiva en vivo" in snippet_data["snippet"]


def test_visual_not_found():
    res = client.get("/visuals/slug-que-no-existe-12345")
    assert res.status_code == 404
