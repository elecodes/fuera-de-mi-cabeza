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


def test_openai_client_raises_instead_of_silently_falling_back_to_mock():
    async def _run():
        # Antes: si fallaban todos los modelos (clave inválida, rate limit,
        # modelo retirado...), generate() devolvía en silencio una respuesta
        # de MockLLMClient como si fuera un borrador real y exitoso. Ahora
        # debe propagar el error real.
        client = OpenAICompatibleClient(
            api_key="test-key",
            model="modelo-principal",
            fallback_models=["modelo-fallback"],
            base_url="https://api.groq.com/openai/v1",
        )

        req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")

        async def mock_post(url, headers, json):
            resp = httpx.Response(status_code=401, json={"error": "Invalid API Key"}, request=req)
            resp.raise_for_status()

        with patch.object(httpx.AsyncClient, "post", side_effect=mock_post):
            with pytest.raises(RuntimeError) as exc_info:
                await client.generate("Hola")

            # El mensaje debe indicar qué modelos se intentaron, no devolver
            # contenido plantilla/mock disfrazado de respuesta exitosa.
            assert "modelo-principal" in str(exc_info.value)
            assert "modelo-fallback" in str(exc_info.value)

    asyncio.run(_run())


def test_openai_client_raises_even_when_groq_direct_retry_also_fails():
    async def _run():
        client = OpenAICompatibleClient(
            api_key="test-key",
            model="modelo-principal",
            fallback_models=[],
            base_url="http://127.0.0.1:20128/v1",  # no es groq.com: dispara el reintento directo
        )

        req = httpx.Request("POST", "http://127.0.0.1:20128/v1/chat/completions")

        async def mock_post(url, headers, json):
            resp = httpx.Response(status_code=500, json={"error": "boom"}, request=req)
            resp.raise_for_status()

        with patch.object(httpx.AsyncClient, "post", side_effect=mock_post), \
             patch.dict("os.environ", {"GROQ_API_KEY": "also-fails-key"}):
            with pytest.raises(RuntimeError):
                await client.generate("Hola")

    asyncio.run(_run())


def test_get_llm_client_omniroute():
    from app.llm.providers import get_llm_client
    with patch.dict("os.environ", {"LLM_PROVIDER": "omniroute"}):
        client = get_llm_client()
        assert isinstance(client, OpenAICompatibleClient)

    with patch.dict("os.environ", {"LLM_PROVIDER": "omnirouter"}):
        client = get_llm_client()
        assert isinstance(client, OpenAICompatibleClient)

