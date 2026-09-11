import os
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "groq":
        base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY", "")
        return OpenAICompatibleClient(api_key=api_key, model=model, base_url=base_url)

    if provider in ("openai", "openai-compatible"):
        return OpenAICompatibleClient()

    return MockLLMClient()


__all__ = ["LLMClient", "MockLLMClient", "OpenAICompatibleClient", "get_llm_client"]
