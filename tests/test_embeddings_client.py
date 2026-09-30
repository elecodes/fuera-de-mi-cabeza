import asyncio

import pytest

from app.services.embeddings_client import GeminiEmbeddingsClient


class _FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


class _FakeHttpClient:
    def __init__(self, response=None, error=None, captured_calls=None):
        self._response = response
        self._error = error
        self.captured_calls = captured_calls if captured_calls is not None else []

    async def post(self, url, json):
        self.captured_calls.append({"url": url, "json": json})
        if self._error:
            raise self._error
        return self._response


def test_embed_returns_values_from_response():
    async def _run():
        fake_response = _FakeResponse({"embedding": {"values": [0.1, 0.2, 0.3]}})
        calls = []
        fake_client = _FakeHttpClient(response=fake_response, captured_calls=calls)
        client = GeminiEmbeddingsClient(api_key="test-key", http_client=fake_client)

        result = await client.embed("hola mundo", task_type="RETRIEVAL_QUERY")

        assert result == [0.1, 0.2, 0.3]
        assert len(calls) == 1
        assert calls[0]["json"]["taskType"] == "RETRIEVAL_QUERY"
        assert "hola mundo" in calls[0]["json"]["content"]["parts"][0]["text"]

    asyncio.run(_run())


def test_embed_raises_without_api_key():
    async def _run():
        client = GeminiEmbeddingsClient(api_key=None, http_client=_FakeHttpClient())
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
            await client.embed("texto")

    asyncio.run(_run())


def test_embed_raises_on_empty_text():
    async def _run():
        client = GeminiEmbeddingsClient(api_key="test-key", http_client=_FakeHttpClient())
        with pytest.raises(RuntimeError, match="vacío"):
            await client.embed("   ")

    asyncio.run(_run())


def test_embed_raises_on_http_error():
    async def _run():
        fake_client = _FakeHttpClient(error=Exception("401 Unauthorized"))
        client = GeminiEmbeddingsClient(api_key="bad-key", http_client=fake_client)
        with pytest.raises(RuntimeError, match="401 Unauthorized"):
            await client.embed("texto")

    asyncio.run(_run())


def test_embed_raises_when_response_missing_values():
    async def _run():
        fake_response = _FakeResponse({"embedding": {}})
        client = GeminiEmbeddingsClient(api_key="test-key", http_client=_FakeHttpClient(response=fake_response))
        with pytest.raises(RuntimeError, match="no devolvió un embedding válido"):
            await client.embed("texto")

    asyncio.run(_run())
