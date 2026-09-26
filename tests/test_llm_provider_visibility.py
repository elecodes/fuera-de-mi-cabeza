from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.llm.providers import get_llm_client
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient

client = TestClient(app)


def test_get_llm_client_groq_selection():
    with patch.dict(
        "os.environ",
        {"LLM_PROVIDER": "groq", "GROQ_API_KEY": "test-key", "LLM_MODEL": "openai/gpt-oss-120b"},
        clear=False,
    ):
        result = get_llm_client()
        assert isinstance(result, OpenAICompatibleClient)


def test_get_llm_client_warns_loudly_when_provider_unrecognized(capsys):
    # Antes, si LLM_PROVIDER no estaba definido o tenía un valor no reconocido,
    # get_llm_client() devolvía MockLLMClient en silencio: ningún log, ningún
    # aviso, nada que permitiera notar que no se estaba usando un LLM real.
    with patch.dict("os.environ", {"LLM_PROVIDER": "esto-no-existe"}, clear=False):
        result = get_llm_client()

    assert isinstance(result, MockLLMClient)
    captured = capsys.readouterr()
    assert "MockLLMClient" in captured.out
    assert "esto-no-existe" in captured.out


def test_system_status_flags_mock_provider():
    with patch.dict("os.environ", {"LLM_PROVIDER": "mock"}, clear=False):
        res = client.get("/api/system/status")
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "mock"
        assert data["is_mock"] is True


def test_system_status_flags_real_provider():
    with patch.dict("os.environ", {"LLM_PROVIDER": "groq", "LLM_MODEL": "openai/gpt-oss-120b"}, clear=False):
        res = client.get("/api/system/status")
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "groq"
        assert data["is_mock"] is False
        assert data["model"] == "openai/gpt-oss-120b"
