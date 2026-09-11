import asyncio
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient


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
