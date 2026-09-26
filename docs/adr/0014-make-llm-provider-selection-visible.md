# 0014. Make LLM Provider Selection Visible

* **Status:** Accepted
* **Date:** 2026-09-26

## Context and Problem Statement

After ADR 0013 fixed the silent fallback to `MockLLMClient` on real-provider failure, the author still reported the exact same symptom (raw ideas pasted into a templated draft, no error) even after confirming the patch was applied and the backend restarted. The remaining explanation is the *other* path into `MockLLMClient`: `get_llm_client()` returns it directly, by design, whenever `LLM_PROVIDER` is unset or doesn't match `"groq"` / `"openai"` / `"openai-compatible"` / `"omniroute"` / `"omnirouter"` — with no log line, no warning, nothing visible. If `.env` isn't loaded from the working directory the server is actually started from (or `LLM_PROVIDER` is set to something unexpected in the shell/system environment), the app quietly runs in mock mode indefinitely, and every endpoint still returns a normal HTTP 200.

This is the same failure class as ADR 0013 (silent, plausible-looking degradation), but one layer higher: it's not a failure being hidden, it's a *configuration outcome* being hidden. `MockLLMClient` is a legitimate, intentional choice for local development without an API key — the problem is only that nothing distinguishes "you asked for mock" from "you didn't realize you're in mock."

## Decision Outcome

1. **`get_llm_client()` now logs (and prints, so it's visible in the terminal running the server) which provider and model it selected**, on every call — for `groq` and `openai-compatible`, a short confirmation line; when it falls through to `MockLLMClient`, a loud warning naming the raw `LLM_PROVIDER` value that caused it, so a misconfigured or unloaded `.env` is visible immediately at request time without needing to reproduce the bug through the UI first.
2. **`/api/system/status` now also returns `model` and an explicit `is_mock` boolean**, so the current provider can be checked from a browser or `curl` without reading server logs at all.

### Positive Consequences

* Diagnosing "why does this look like it worked but the content is wrong" now takes one `curl` or one glance at the server terminal, instead of a multi-turn investigation.

### Considered but Not Done

* Did not change the *default* behavior (unset/unrecognized `LLM_PROVIDER` still resolves to `MockLLMClient`) — mock-by-default is a reasonable choice for a fresh checkout with no `.env` at all, and changing it to raise would break that flow. The fix here is visibility, not a different default.
