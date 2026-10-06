# 0025. Lightweight Observability for LLM Calls

* **Status:** Accepted
* **Date:** 2026-10-03

## Context and Problem Statement

ADR 0024 considered Genkit as an orchestration framework and specifically identified observability — a way to inspect each pipeline step's prompt and response — as the one genuine gap in the project's current setup, while recommending against adopting a whole Alpha-stage framework just for that one need. This ADR implements that narrower recommendation directly.

Throughout this project's development, diagnosing "why did this draft turn out this way" has been done by hand: reading prompt template files and `system_prompt` strings line by line, asking the author to paste example output, and reasoning from there. A lightweight, always-on log of each LLM call removes most of that friction.

## Decision Outcome

1. **`app/services/tracer.py`**: `log_llm_call(...)` appends one JSON object per LLM call to `data/traces.jsonl` (gitignored — local debugging data, same treatment as `data/sessions/` and `data/knowledge_base.json`), capping the file at the most recent 300 entries (`MAX_TRACES_KEPT`) so it never grows unbounded. Each entry captures the step name, model (when the client exposes one), duration in milliseconds, truncated previews (4000 chars) of the prompt/system prompt/response, and the error message if the call failed.
2. **`traced_generate(llm_client, step, prompt, system_prompt)`**: a thin wrapper around `llm_client.generate(...)` that times the call and logs it, then returns the response (or re-raises the original exception) exactly as the unwrapped call would have. All 10 call sites across every service (`idea_explorer`, `content_planner`, `draft_generator` ×2, `voice_auditor`, `voice_editor` ×2, `argument_griller`, `profile_generator`) now go through this wrapper instead of calling `llm_client.generate(...)` directly, each tagged with its own step name (e.g. `"draft_generator.generate_note"`).
3. **Observability is auxiliary, not critical — the opposite failure mode from the rest of this project.** Every other part of this codebase deliberately fails loud (ADR 0009, 0012, 0013): a broken dependency should never silently degrade into a wrong-looking success. Tracing inverts that on purpose: if writing a trace entry fails for any reason, it's swallowed silently inside `log_llm_call`, because a debugging aid must never be able to break the real pipeline it's observing. This mirrors the same reasoning already used for the "related pieces" RAG notice (ADR 0020), which also fails silently since it's informational, not core functionality.
4. **`GET /api/traces?limit=N`**: returns the most recent traces, newest first. No configuration needed — it works from first boot, returning an empty list until the first LLM call happens.
5. **UI**: a "🔬 Observabilidad" toggle in the header opens a panel listing recent calls (step, duration, status) as collapsible `<details>` elements, each expandable to show the full system prompt, prompt, and response.

### Positive Consequences

* Diagnosing a voice/quality issue (the kind this project has repeatedly worked through this session) now takes opening a panel in the browser, not asking the author to paste examples back and forth.
* No new dependency, no separate service, no schema — a single append-only JSON Lines file.

### Considered but Not Done

* Did not thread `session_id` through every service call to tag traces by session — this would have required changing most service method signatures, for marginal benefit given the step name and timestamp already make a trace easy to correlate with recent activity. Can be added later if filtering by session becomes genuinely needed.
* Did not store full (untruncated) prompts/responses — 4000-character previews are enough to diagnose almost any issue while keeping the trace file small; this is a debugging aid, not an audit log.
* Superseded by, and replaces, the Genkit-for-observability option raised in ADR 0024.
