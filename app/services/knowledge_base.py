import json
import math
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base.json"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeBase:
    """
    Almacén local de piezas ya publicadas, para buscar por similitud de
    significado (no de palabras) contra una idea nueva.

    Nada de base de datos vectorial: a la escala de un catálogo personal
    (decenas o cientos de piezas), un JSON y una comparación de coseno en
    Python puro son más que suficientes, y no añaden infraestructura.
    """

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path else DEFAULT_PATH

    def _load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_modified_time(self, doc_id: str) -> str | None:
        """Para saltar la reindexación de un documento que no ha cambiado en Drive."""
        entry = self._load().get(doc_id)
        return entry.get("modified_time") if entry else None

    def add_or_update(
        self,
        doc_id: str,
        title: str,
        text: str,
        embedding: list[float],
        source_link: str,
        modified_time: str | None = None,
    ) -> None:
        data = self._load()
        data[doc_id] = {
            "title": title,
            "text": text,
            "embedding": embedding,
            "source_link": source_link,
            "modified_time": modified_time,
        }
        self._save(data)

    def remove(self, doc_id: str) -> None:
        data = self._load()
        if doc_id in data:
            del data[doc_id]
            self._save(data)

    def all_documents(self) -> list[dict]:
        return [{"doc_id": doc_id, **entry} for doc_id, entry in self._load().items()]

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        results = []
        for doc_id, entry in self._load().items():
            score = _cosine_similarity(query_embedding, entry.get("embedding", []))
            results.append({
                "doc_id": doc_id,
                "title": entry.get("title"),
                "source_link": entry.get("source_link"),
                "score": score,
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]
