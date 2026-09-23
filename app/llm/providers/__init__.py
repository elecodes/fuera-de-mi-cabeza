import os
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient


def get_llm_client() -> LLMClient:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "groq":
        base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        model = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
        
        env_fallbacks = os.getenv("LLM_FALLBACK_MODELS")
        if env_fallbacks is not None:
            fallback_models = [m.strip() for m in env_fallbacks.split(",") if m.strip()]
        else:
            fallback_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]

        api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY", "")
        return OpenAICompatibleClient(
            api_key=api_key,
            model=model,
            fallback_models=fallback_models,
            base_url=base_url,
        )

    if provider in ("openai", "openai-compatible", "omniroute", "omnirouter"):
        base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:20128/v1")
        model = os.getenv("LLM_MODEL", "auto/best-chat")
        env_fallbacks = os.getenv("LLM_FALLBACK_MODELS")
        if env_fallbacks is not None:
            fallback_models = [m.strip() for m in env_fallbacks.split(",") if m.strip()]
        else:
            fallback_models = ["auto/smart", "auto/fast", "auto/best-free", "auto/chat", "oc/nemotron-3.5-lightning-free"]
        return OpenAICompatibleClient(
            model=model,
            fallback_models=fallback_models,
            base_url=base_url,
        )

    return MockLLMClient()


__all__ = ["LLMClient", "MockLLMClient", "OpenAICompatibleClient", "get_llm_client"]
