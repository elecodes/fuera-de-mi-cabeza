# 0013. Never Silently Fall Back to MockLLMClient on Real Provider Failure

* **Status:** Accepted
* **Date:** 2026-09-25

## Context and Problem Statement

The author reported that generated drafts contained her own raw ideas and answers pasted almost verbatim, wrapped in a thin templated shell, instead of being rewritten in her voice. `LLM_PROVIDER`, `GROQ_API_KEY`, and the configured model/fallback models in `.env` were all correctly set, which ruled out the obvious "no key configured" explanation.

The actual cause was in `OpenAICompatibleClient.generate()`: if every candidate model (the primary model, all `LLM_FALLBACK_MODELS`, and a same-provider "Groq Direct" retry) raised an exception — an invalid or rate-limited API key, a timeout, a deprecated model ID, a malformed response — the method caught the final failure and silently returned `MockLLMClient().generate(...)` instead of raising. `MockLLMClient` is a heuristic text generator meant for local development without an API key: for Note and Article generation, it builds a templated paragraph around the raw idea/answers text extracted from the prompt (see `app/llm/providers/mock.py`), which is close to a direct paste of the author's own input.

The result: every endpoint that calls `generate()` received a normal-looking string and returned HTTP 200. There was no error, no log the author would see, and no way to tell — from the app's behavior alone — that the real LLM was never actually reached. A transient Groq failure (rate limit, momentary outage, an expired key) silently degraded every draft to a template wrapped around the author's own raw notes, indistinguishable from a successful generation.

A secondary, related bug was also found: `openai_client.py` calls `json.loads(...)` in its SSE-stream-parsing branch but never imports the `json` module, which would raise `NameError` if that code path were ever exercised (e.g., a provider that streams SSE-formatted chunks even with `"stream": False` requested).

## Decision Drivers

* **Visibility over graceful degradation**: a silent fallback that produces plausible-looking but wrong output is worse than a visible error, because the person has no way to know something went wrong.
* **Consistency**: this is the same failure pattern already fixed in ADR 0009 (`VoiceEditor` saving raw feedback as a "rule" on synthesis failure) and ADR 0012 (`ArgumentGriller` returning generic fallback questions on JSON parse failure). `OpenAICompatibleClient` is the highest-impact instance of the same anti-pattern, since it affects every single draft, note, revision, plan, and question generated through the real provider.

## Decision Outcome

1. **`OpenAICompatibleClient.generate()` no longer imports or calls `MockLLMClient` under any circumstance.** If every candidate model fails, and the same-provider direct retry (when applicable) also fails, it raises `RuntimeError` with the list of models attempted and the last underlying exception attached as the cause (`raise ... from last_exception`), instead of returning a string.
2. Every caller of `generate()` (`IdeaExplorer`, `ContentPlanner`, `DraftGenerator`, `VoiceEditor`, `VoiceAuditor`, `ArgumentGriller`) reaches this through service methods that `app/main.py`'s endpoints already wrap in `try/except Exception as e: raise HTTPException(status_code=500, detail=f"...: {str(e)}")`. No endpoint code changed: the fix makes the *real* error (e.g. "401 Unauthorized", a rate-limit message, a timeout) visible in that same HTTP 500 response, instead of a fake 200 success.
3. **`MockLLMClient` is now reached only when explicitly requested** — either directly in tests, or via `LLM_PROVIDER=mock` (or an unset/unrecognized `LLM_PROVIDER`) in `get_llm_client()` — never as a hidden fallback from a real provider's failure.
4. Fixed the missing `import json` in `openai_client.py`.

### Positive Consequences

* A failing draft generation now surfaces a real, actionable error message instead of a fake success.
* No more risk of an author publishing a "draft" that is actually her own raw notes lightly templated, believing it came from the LLM.

### Negative Consequences

* Endpoints that previously always returned 200 (even during a provider outage) will now return 500 during a genuine outage. This is intentional: a visible failure is preferable to an invisible, wrong success.
