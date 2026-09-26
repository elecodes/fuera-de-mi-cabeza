import json
import os
import logging
import httpx

logger = logging.getLogger(__name__)


class OpenAICompatibleClient:
    """
    Cliente genérico compatible con OpenAI / Ollama / Groq usando HTTPX,
    con soporte automático para reintentos mediante modelos de fallback.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        fallback_models: list[str] | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        
        if fallback_models is not None:
            self.fallback_models = fallback_models
        else:
            env_fallbacks = os.getenv("LLM_FALLBACK_MODELS", "")
            self.fallback_models = [m.strip() for m in env_fallbacks.split(",") if m.strip()]

        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        candidate_models = [self.model] + [m for m in self.fallback_models if m != self.model]

        last_exception = None

        async with httpx.AsyncClient(timeout=35.0) as client:
            for idx, current_model in enumerate(candidate_models):
                payload = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": 0.7,
                    "stream": False,
                }
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    response.raise_for_status()
                    text = response.text.strip()
                    if text.startswith("data:"):
                        # Handling SSE stream format from proxy routers
                        parts = []
                        for line in text.splitlines():
                            line = line.strip()
                            if line.startswith("data: ") and line != "data: [DONE]":
                                try:
                                    chunk = json.loads(line[6:].strip())
                                    choices = chunk.get("choices", [])
                                    if choices:
                                        delta_content = choices[0].get("delta", {}).get("content")
                                        msg_content = choices[0].get("message", {}).get("content")
                                        parts.append(delta_content or msg_content or "")
                                except Exception:
                                    continue
                        return "".join(parts)
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                except Exception as err:
                    last_exception = err
                    next_model = candidate_models[idx + 1] if idx + 1 < len(candidate_models) else None
                    if next_model:
                        logger.warning(
                            f"[LLM Fallback] Error con modelo '{current_model}': {err}. Intentando con fallback '{next_model}'..."
                        )
                        print(
                            f"⚠️ [LLM Fallback] Error con '{current_model}': {err}. Reintentando con '{next_model}'..."
                        )
                    else:
                        logger.error(f"[LLM Error] Fallaron todos los modelos candidata: {candidate_models}")

        if last_exception:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key and "groq.com" not in self.base_url:
                logger.warning(
                    f"[LLM Fallback to Groq Direct] Error con '{self.base_url}' ({last_exception}). Reintentando con Groq API..."
                )
                print(
                    f"⚠️ [LLM Fallback to Groq Direct] Error conectando a '{self.base_url}'. Reintentando directamente vía Groq API..."
                )
                try:
                    groq_client = OpenAICompatibleClient(
                        api_key=groq_key,
                        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
                        fallback_models=["llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                        base_url="https://api.groq.com/openai/v1",
                    )
                    return await groq_client.generate(prompt, system_prompt=system_prompt)
                except Exception as groq_err:
                    logger.error(f"[LLM Error Groq Direct] {groq_err}")
                    last_exception = groq_err

            # IMPORTANTE: nunca caer en silencio al MockLLMClient aquí. Antes, si
            # fallaban todos los modelos (clave inválida, modelo retirado, rate
            # limit, timeout...), esta función devolvía una respuesta del mock
            # como si fuera un borrador real generado con éxito: la persona
            # recibía un HTTP 200 con sus propias notas pegadas dentro de una
            # plantilla, sin ningún indicio de que el LLM real nunca respondió.
            # Ahora se propaga el error real, para que se vea en la interfaz
            # (y en los logs) qué falló de verdad.
            attempted = ", ".join(candidate_models)
            raise RuntimeError(
                f"No se pudo obtener respuesta de ningún modelo LLM configurado ({attempted}). "
                f"Último error: {last_exception}"
            ) from last_exception

        raise RuntimeError(
            "No se pudo obtener respuesta del LLM: no se intentó ningún modelo candidato."
        )

