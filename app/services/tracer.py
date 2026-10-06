import json
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TRACES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "traces.jsonl"
MAX_TRACES_KEPT = 300
_PREVIEW_CHARS = 4000

"""
Observabilidad ligera: en vez de adoptar un framework de orquestación (ver
ADR 0024, por qué Genkit no encaja aquí ahora mismo), esto registra cada
llamada al LLM en un JSON Lines local (data/traces.jsonl, gitignored) — qué
prompt entró, qué salió, cuánto tardó, si falló. Se ve desde el panel
"🔬 Observabilidad" de la web o leyendo el archivo directamente.

Principio importante: una traza nunca debe romper el flujo real. Si escribir
la traza falla (disco lleno, lo que sea), se ignora en silencio — a
diferencia del resto del proyecto, que falla alto a propósito (ADR 0009,
0012, 0013), aquí el registro es auxiliar, no crítico, igual que el aviso de
"ya escribiste algo parecido" del RAG (ADR 0020).
"""


def _trim_traces(path: Path, max_lines: int = MAX_TRACES_KEPT) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > max_lines:
        path.write_text("\n".join(lines[-max_lines:]) + "\n", encoding="utf-8")


def log_llm_call(
    step: str,
    prompt: str,
    system_prompt: str | None,
    response: str | None,
    duration_ms: int,
    error: str | None = None,
    model: str | None = None,
    path: Path | str | None = None,
) -> None:
    trace_path = Path(path) if path else DEFAULT_TRACES_PATH
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "model": model,
        "duration_ms": duration_ms,
        "prompt_preview": (prompt or "")[:_PREVIEW_CHARS],
        "system_prompt_preview": (system_prompt or "")[:_PREVIEW_CHARS],
        "response_preview": (response or "")[:_PREVIEW_CHARS] if response is not None else None,
        "error": error,
    }
    try:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        with trace_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        _trim_traces(trace_path)
    except Exception:
        pass  # la traza nunca debe romper el flujo real


async def traced_generate(
    llm_client,
    step: str,
    prompt: str,
    system_prompt: str | None = None,
    path: Path | str | None = None,
) -> str:
    """
    Llama a llm_client.generate(...) igual que siempre, y además registra la
    llamada para observabilidad. Si llm_client.generate() falla, la
    excepción se relanza tal cual (el registro no cambia ese comportamiento);
    solo se añade una traza con el error antes de relanzar.
    """
    start = time.monotonic()
    response: str | None = None
    error: str | None = None
    try:
        response = await llm_client.generate(prompt=prompt, system_prompt=system_prompt)
        return response
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration_ms = int((time.monotonic() - start) * 1000)
        model = getattr(llm_client, "model", None)
        log_llm_call(
            step=step,
            prompt=prompt,
            system_prompt=system_prompt,
            response=response,
            duration_ms=duration_ms,
            error=error,
            model=model,
            path=path,
        )


def read_recent_traces(limit: int = 50, path: Path | str | None = None) -> list[dict]:
    """Devuelve las trazas más recientes, la más nueva primero."""
    trace_path = Path(path) if path else DEFAULT_TRACES_PATH
    if not trace_path.exists():
        return []
    lines = trace_path.read_text(encoding="utf-8").splitlines()
    recent = lines[-limit:]
    traces = []
    for line in reversed(recent):
        try:
            traces.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return traces
