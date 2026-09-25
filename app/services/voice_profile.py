from pathlib import Path

from app.memory.editorial_memory import EditorialMemory

_PLACEHOLDER_MARKER = "[Pega aquí"


def load_voice_profile(
    editorial_memory: EditorialMemory | None = None,
    profile_path: Path | str | None = None,
    base_dir: Path | None = None,
) -> str:
    """
    Construye el contexto de voz que se inyecta en los prompts:

    1. data/voice_guide.md (guía de cómo escribe la autora). Si no existe,
       cae de vuelta a data/editorial_profile.md como fallback histórico.
    2. data/voice_samples.md, si existe y no es el placeholder sin rellenar.
    3. Las reglas aprendidas de data/editorial_memory.json.

    Todos los servicios que redactan, revisan, auditan o formulan preguntas
    deben usar esta misma función para que trabajen con la misma definición
    de la voz de la autora.
    """
    base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
    guide_path = base_dir / "data" / "voice_guide.md"
    samples_path = base_dir / "data" / "voice_samples.md"
    fallback_profile_path = Path(profile_path) if profile_path else base_dir / "data" / "editorial_profile.md"

    parts: list[str] = []
    if guide_path.exists():
        parts.append(guide_path.read_text(encoding="utf-8"))
    elif fallback_profile_path.exists():
        parts.append(fallback_profile_path.read_text(encoding="utf-8"))
    else:
        parts.append("Perfil Editorial no especificado.")

    if samples_path.exists():
        samples_content = samples_path.read_text(encoding="utf-8").strip()
        if samples_content and _PLACEHOLDER_MARKER not in samples_content:
            parts.append(f"## Muestras Reales de Voz del Autor:\n{samples_content}")

    memory = editorial_memory if editorial_memory is not None else EditorialMemory()
    memory_ctx = memory.get_context()
    if memory_ctx:
        parts.append(memory_ctx)

    return "\n\n".join(parts)
