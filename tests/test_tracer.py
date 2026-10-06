import asyncio
import json

import pytest

from app.llm.providers.mock import MockLLMClient
from app.services.tracer import log_llm_call, read_recent_traces, traced_generate


def test_log_llm_call_writes_a_jsonl_entry(tmp_path):
    trace_path = tmp_path / "traces.jsonl"

    log_llm_call(
        step="idea_explorer.analyze",
        prompt="un prompt de prueba",
        system_prompt="un system prompt",
        response="una respuesta",
        duration_ms=123,
        model="openai/gpt-oss-120b",
        path=trace_path,
    )

    lines = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["step"] == "idea_explorer.analyze"
    assert entry["duration_ms"] == 123
    assert entry["model"] == "openai/gpt-oss-120b"
    assert "un prompt de prueba" in entry["prompt_preview"]
    assert entry["error"] is None


def test_log_llm_call_truncates_long_text(tmp_path):
    trace_path = tmp_path / "traces.jsonl"
    long_text = "x" * 10000

    log_llm_call(
        step="draft_generator.generate_note",
        prompt=long_text,
        system_prompt=None,
        response=long_text,
        duration_ms=10,
        path=trace_path,
    )

    entry = json.loads(trace_path.read_text(encoding="utf-8").splitlines()[0])
    assert len(entry["prompt_preview"]) <= 4000
    assert len(entry["response_preview"]) <= 4000


def test_log_llm_call_never_raises_when_write_fails(tmp_path):
    # Un directorio como "archivo" de trazas hace que la escritura falle;
    # el registro nunca debe romper el flujo real, solo se ignora.
    bad_path = tmp_path / "a-directory"
    bad_path.mkdir()

    log_llm_call(
        step="x", prompt="p", system_prompt=None, response="r", duration_ms=1, path=bad_path
    )  # no debe lanzar


def test_read_recent_traces_returns_newest_first(tmp_path):
    trace_path = tmp_path / "traces.jsonl"
    for i in range(3):
        log_llm_call(
            step=f"step-{i}", prompt="p", system_prompt=None, response="r", duration_ms=i, path=trace_path
        )

    traces = read_recent_traces(limit=10, path=trace_path)

    assert [t["step"] for t in traces] == ["step-2", "step-1", "step-0"]


def test_read_recent_traces_respects_limit(tmp_path):
    trace_path = tmp_path / "traces.jsonl"
    for i in range(5):
        log_llm_call(step=f"step-{i}", prompt="p", system_prompt=None, response="r", duration_ms=i, path=trace_path)

    traces = read_recent_traces(limit=2, path=trace_path)

    assert len(traces) == 2
    assert traces[0]["step"] == "step-4"


def test_read_recent_traces_on_missing_file_returns_empty(tmp_path):
    assert read_recent_traces(path=tmp_path / "no-existe.jsonl") == []


def test_trim_keeps_only_most_recent_entries(tmp_path):
    trace_path = tmp_path / "traces.jsonl"
    for i in range(350):
        log_llm_call(step=f"step-{i}", prompt="p", system_prompt=None, response="r", duration_ms=i, path=trace_path)

    lines = trace_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 300
    # Se conservan las más recientes, no las más antiguas.
    last_entry = json.loads(lines[-1])
    assert last_entry["step"] == "step-349"


def test_traced_generate_logs_and_returns_response(tmp_path):
    async def _run():
        trace_path = tmp_path / "traces.jsonl"
        mock_llm = MockLLMClient(default_response="una respuesta de prueba")

        result = await traced_generate(
            mock_llm, "idea_explorer.analyze", "mi prompt", "mi system prompt", path=trace_path
        )

        assert result == "una respuesta de prueba"
        traces = read_recent_traces(path=trace_path)
        assert len(traces) == 1
        assert traces[0]["step"] == "idea_explorer.analyze"
        assert traces[0]["error"] is None

    asyncio.run(_run())


def test_traced_generate_logs_error_and_reraises(tmp_path):
    async def _run():
        trace_path = tmp_path / "traces.jsonl"

        class _FailingClient:
            async def generate(self, prompt, system_prompt=None):
                raise RuntimeError("falló el LLM real")

        with pytest.raises(RuntimeError, match="falló el LLM real"):
            await traced_generate(_FailingClient(), "draft_generator.generate_note", "p", "s", path=trace_path)

        traces = read_recent_traces(path=trace_path)
        assert len(traces) == 1
        assert traces[0]["error"] == "falló el LLM real"
        assert traces[0]["response_preview"] is None

    asyncio.run(_run())
