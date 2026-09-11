import os
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider in ("openai", "openai-compatible"):
        return OpenAICompatibleClient()
    return MockLLMClient()


__all__ = ["LLMClient", "MockLLMClient", "OpenAICompatibleClient", "get_llm_client"]
