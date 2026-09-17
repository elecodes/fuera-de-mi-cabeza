import asyncio
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient


def test_mock_llm_client_default_response():
    async def _run():
        client: LLMClient = MockLLMClient(default_response='{"status": "ok"}')
        res = await client.generate(prompt="Hola", system_prompt="Sys")
        assert res == '{"status": "ok"}'

    asyncio.run(_run())


def test_mock_llm_client_history():
    async def _run():
        mock = MockLLMClient(default_response="Response")
        await mock.generate("Prompt 1", system_prompt="Sys 1")
        assert len(mock.call_history) == 1
        assert mock.call_history[0]["prompt"] == "Prompt 1"
        assert mock.call_history[0]["system_prompt"] == "Sys 1"

    asyncio.run(_run())


def test_openai_client_fallback_retry():
    async def _run():
        client = OpenAICompatibleClient(
            api_key="test-key",
            model="llama-3.3-70b-versatile",
            fallback_models=["openai/gpt-oss-120b", "qwen/qwen3.6-27b"],
            base_url="https://api.groq.com/openai/v1",
        )

        attempts = []
        req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")

        async def mock_post(url, headers, json):
            model_called = json["model"]
            attempts.append(model_called)
            if model_called == "llama-3.3-70b-versatile":
                # Simular falla en el modelo primario
                resp = httpx.Response(status_code=429, json={"error": "Rate limit exceeded"}, request=req)
                resp.raise_for_status()
            # Éxito en el primer fallback
            return httpx.Response(
                status_code=200,
                json={"choices": [{"message": {"content": "Respuesta de fallback"}}]},
                request=req,
            )

        with patch.object(httpx.AsyncClient, "post", side_effect=mock_post):
            res = await client.generate("Hola")
            assert res == "Respuesta de fallback"
            assert attempts == ["llama-3.3-70b-versatile", "openai/gpt-oss-120b"]

    asyncio.run(_run())


def test_get_llm_client_omniroute():
    from app.llm.providers import get_llm_client
    with patch.dict("os.environ", {"LLM_PROVIDER": "omniroute"}):
        client = get_llm_client()
        assert isinstance(client, OpenAICompatibleClient)

    with patch.dict("os.environ", {"LLM_PROVIDER": "omnirouter"}):
        client = get_llm_client()
        assert isinstance(client, OpenAICompatibleClient)

