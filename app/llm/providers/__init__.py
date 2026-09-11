import os
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "groq":
        base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        env_fallbacks = os.getenv("LLM_FALLBACK_MODELS")
        if env_fallbacks is not None:
            fallback_models = [m.strip() for m in env_fallbacks.split(",") if m.strip()]
        else:
            fallback_models = ["openai/gpt-oss-120b", "qwen/qwen3.6-27b"]

        api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY", "")
        return OpenAICompatibleClient(
            api_key=api_key,
            model=model,
            fallback_models=fallback_models,
            base_url=base_url,
        )

    if provider in ("openai", "openai-compatible"):
        return OpenAICompatibleClient()

    return MockLLMClient()


__all__ = ["LLMClient", "MockLLMClient", "OpenAICompatibleClient", "get_llm_client"]
