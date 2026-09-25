import difflib
import json
from pathlib import Path


class EditorialMemory:
    """
    Servicio de gestión de memoria editorial persistente (data/editorial_memory.json).
    Almacena y organiza expresiones favoritas, muletillas personales, palabras prohibidas
    y reglas de estilo aprendidas a través del feedback continuo del autor.
    """

    DEFAULT_CATEGORIES = [
        "favorite_expressions",
        "forbidden_words",
        "opening_styles",
        "rhythm_rules",
        "likes",
        "dislikes",
        "style_rules",
        "recurring_themes",
        "preferred_structures",
        "words_to_avoid",
        "examples",
    ]

    CATEGORY_LABELS = {
        "favorite_expressions": "Expresiones y muletillas favoritas",
        "forbidden_words": "Palabras y tics a evitar",
        "opening_styles": "Estilos de apertura preferidos",
        "rhythm_rules": "Reglas de ritmo y cadencia",
        "style_rules": "Reglas de estilo aprendidas",
        "likes": "Gustos de redacción",
        "dislikes": "Rechazos explícitos",
        "recurring_themes": "Temas recurrentes",
        "preferred_structures": "Estructuras preferidas",
        "words_to_avoid": "Palabras prohibidas adicionales",
        "examples": "Ejemplos de frases del autor",
    }

    def __init__(self, memory_file: Path | str | None = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.memory_file = Path(memory_file) if memory_file else base_dir / "data" / "editorial_memory.json"
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        if not self.memory_file.exists():
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = {cat: [] for cat in self.DEFAULT_CATEGORIES}
            self.memory_file.write_text(json.dumps(initial_data, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            # Asegurar que todas las categorías por defecto existan
            try:
                data = json.loads(self.memory_file.read_text(encoding="utf-8"))
                updated = False
                for cat in self.DEFAULT_CATEGORIES:
                    if cat not in data or not isinstance(data[cat], list):
                        data[cat] = []
                        updated = True
                if updated:
                    self.memory_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                initial_data = {cat: [] for cat in self.DEFAULT_CATEGORIES}
                self.memory_file.write_text(json.dumps(initial_data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_all_memory(self) -> dict[str, list[str]]:
        if not self.memory_file.exists():
            self._ensure_storage()
        try:
            return json.loads(self.memory_file.read_text(encoding="utf-8"))
        except Exception:
            return {cat: [] for cat in self.DEFAULT_CATEGORIES}

    def get_context(self) -> str:
        data = self.get_all_memory()
        lines = []

        if any(data.values()):
            lines.append("## Memoria de Voz y Estilo Personal del Autor (APLICAR OBLIGATORIAMENTE):")

            for cat, label in self.CATEGORY_LABELS.items():
                items = data.get(cat, [])
                if items:
                    formatted_items = "; ".join(f"'{item}'" for item in items)
                    lines.append(f"- **{label}:** {formatted_items}")

        return "\n".join(lines)

    _DUPLICATE_SIMILARITY_THRESHOLD = 0.8

    def add_preference(self, category: str, preference: str) -> None:
        if not preference or not preference.strip():
            return
        if not self.memory_file.exists():
            self._ensure_storage()
        try:
            data = self.get_all_memory()
            if category not in data:
                data[category] = []
            clean_pref = preference.strip()
            is_duplicate = any(
                difflib.SequenceMatcher(None, clean_pref.lower(), existing.lower()).ratio()
                >= self._DUPLICATE_SIMILARITY_THRESHOLD
                for existing in data[category]
            )
            if not is_duplicate:
                data[category].append(clean_pref)
            self.memory_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Error actualizando memoria editorial: {e}")

    def delete_preference(self, category: str, preference: str) -> bool:
        if not self.memory_file.exists():
            return False
        try:
            data = self.get_all_memory()
            if category in data and preference in data[category]:
                data[category].remove(preference)
                self.memory_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                return True
            return False
        except Exception as e:
            print(f"Error eliminando de la memoria editorial: {e}")
            return False
