import os

import httpx

DEFAULT_MODEL = "gemini-embedding-001"
DEFAULT_DIMENSIONS = 768
_API_BASE = "https://generativelanguage.googleapis.com/v1beta"


class GeminiEmbeddingsClient:
    """
    Cliente ligero para la API de embeddings de Gemini (tiene tier gratuito).

    No usa el SDK `google-generativeai`: es una única llamada HTTP, así que
    se hace directamente con httpx (que el proyecto ya usa en
    `app/llm/providers/openai_client.py`), sin añadir una dependencia nueva.

    `task_type` importa para la calidad de la búsqueda: "RETRIEVAL_DOCUMENT"
    al indexar piezas ya publicadas, "RETRIEVAL_QUERY" al buscar a partir de
    una idea nueva — son espacios vectoriales optimizados de forma distinta
    para cada lado de una búsqueda asimétrica.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
        http_client: httpx.AsyncClient | None = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_EMBEDDING_MODEL", DEFAULT_MODEL)
        self.dimensions = dimensions or int(os.getenv("GEMINI_EMBEDDING_DIMENSIONS", DEFAULT_DIMENSIONS))
        self._http_client = http_client  # inyectable para tests

    async def embed(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY no está configurado. Añade tu clave de la API de Gemini en tu .env."
            )
        if not text or not text.strip():
            raise RuntimeError("No se puede generar un embedding de un texto vacío.")

        url = f"{_API_BASE}/models/{self.model}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{self.model}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
            "outputDimensionality": self.dimensions,
        }

        client = self._http_client or httpx.AsyncClient(timeout=30.0)
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Error al generar el embedding con Gemini: {e}") from e
        finally:
            if self._http_client is None:
                await client.aclose()

        data = response.json()
        values = data.get("embedding", {}).get("values")
        if not values:
            raise RuntimeError(f"Gemini no devolvió un embedding válido: {data}")
        return values
