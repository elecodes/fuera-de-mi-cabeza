import os
import logging
from app.llm.client import LLMClient
from app.llm.providers.mock import MockLLMClient
from app.llm.providers.openai_client import OpenAICompatibleClient

logger = logging.getLogger(__name__)


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
        _log_provider_selection("groq", model, has_key=bool(api_key))
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
        _log_provider_selection(provider, model, has_key=True)
        return OpenAICompatibleClient(
            model=model,
            fallback_models=fallback_models,
            base_url=base_url,
        )

    # IMPORTANTE: llegar aquí significa que LLM_PROVIDER no está puesto o no se
    # reconoce ("groq", "openai", "openai-compatible", "omniroute", "omnirouter"
    # son los únicos valores que activan un proveedor real). El resultado es
    # MockLLMClient: respuestas heurísticas de plantilla, no un LLM real. Esto
    # puede pasar en silencio si el .env no se carga desde donde arranca el
    # servidor (working directory distinto, variable de entorno ya puesta con
    # otro valor en el sistema, etc.), así que se avisa fuerte por consola:
    # ningún endpoint devuelve error en este caso, así que sin este aviso no
    # hay forma de notar que se está usando el simulador en vez del LLM real.
    logger.warning(
        f"[LLM Provider] LLM_PROVIDER='{os.getenv('LLM_PROVIDER')}' no reconocido o no definido. "
        "Usando MockLLMClient: las respuestas serán heurísticas de plantilla, NO generadas por un LLM real."
    )
    print(
        f"⚠️  [LLM Provider] LLM_PROVIDER={os.getenv('LLM_PROVIDER')!r} no reconocido o no definido. "
        "USANDO MockLLMClient (respuestas simuladas, no un LLM real). "
        "Si esperabas usar Groq/OmniRoute, revisa que el .env se cargue desde esta carpeta."
    )
    return MockLLMClient()


def _log_provider_selection(provider: str, model: str, has_key: bool) -> None:
    key_note = "" if has_key else " ⚠️ SIN CLAVE CONFIGURADA"
    logger.info(f"[LLM Provider] Usando '{provider}' con modelo '{model}'{key_note}")
    print(f"🔧 [LLM Provider] Usando '{provider}' con modelo '{model}'{key_note}")


__all__ = ["LLMClient", "MockLLMClient", "OpenAICompatibleClient", "get_llm_client"]
