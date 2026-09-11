import json
from pathlib import Path


class EditorialMemory:
    """
    Interfaz preparatoria para la memoria editorial (MVP 0.2).
    En v0.1 no realiza aprendizaje automático, pero provee métodos para
    guardar y recuperar preferencias futuras.
    """

    def __init__(self, memory_file: Path | str | None = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.memory_file = Path(memory_file) if memory_file else base_dir / "data" / "editorial_memory.json"
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.memory_file.exists():
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = {
                "likes": [],
                "dislikes": [],
                "style_rules": [],
                "recurring_themes": [],
                "preferred_structures": [],
                "words_to_avoid": [],
                "examples": [],
            }
            self.memory_file.write_text(json.dumps(initial_data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_context(self) -> str:
        if not self.memory_file.exists():
            return ""
        try:
            data = json.loads(self.memory_file.read_text(encoding="utf-8"))
            lines = []
            for key, val in data.items():
                if val:
                    lines.append(f"{key}: {', '.join(val)}")
            return "\n".join(lines)
        except Exception:
            return ""

    def add_preference(self, category: str, preference: str) -> None:
        if not self.memory_file.exists():
            self._ensure_storage()
        try:
            data = json.loads(self.memory_file.read_text(encoding="utf-8"))
            if category not in data:
                data[category] = []
            if preference not in data[category]:
                data[category].append(preference)
            self.memory_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Error actualizando memoria editorial: {e}")
