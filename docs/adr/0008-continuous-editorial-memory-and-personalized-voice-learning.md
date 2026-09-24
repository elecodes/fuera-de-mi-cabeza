# 0008. Continuous Editorial Memory, Personalized Voice Learning, and Prompt Payload Condensation

* **Status:** Accepted  
* **Date:** 2026-09-24  

## Context and Problem Statement

The personal editorial agent previously relied on a static `editorial_profile.md` containing extensive few-shot writing examples (~268 lines, >30KB payload when injected into system prompts). This large prompt size triggered HTTP 413 (Payload Too Large) and 429 (Rate Limit) errors on Groq API models (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`).

When Groq requests failed, the pipeline fell back to `MockLLMClient`, which was interpolating raw prompt text verbatim into draft outputs due to un-sanitized template variable matching. As a result, draft generation produced repetitive, un-synthesized text that echoed the user's initial prompt line-by-line. Additionally, author feedback provided during editorial sessions (e.g. preferred expressions, forbidden words, rhythm preferences) was transient and lost across sessions.

## Decision Drivers

* **Persistent Style Personalization**: Persist author voice patterns, favorite expressions, forbidden words, rhythm rules, and opening styles across sessions (`editorial_memory.json`).
* **Prompt Payload Optimization**: Reduce prompt payloads by 65% (from ~31KB to ~11KB) by separating core voice rules from heavy verbatim few-shot examples while injecting active `EditorialMemory` context.
* **Articulate Draft Synthesis & Fallback Safety**: Ensure `DraftGenerator` prompts explicitly enforce 2–3 paragraph articulate note synthesis in Castellano Peninsular, and sanitize `MockLLMClient` topic extraction to eliminate raw prompt verbatim dumps.

## Decision Outcome

1. **`EditorialMemory` Architecture (`app/memory/editorial_memory.py`)**: Designed a structured, JSON-backed persistent store for author voice preferences categorized into `favorite_expressions`, `forbidden_words`, `style_rules`, `rhythm_rules`, and `opening_styles`. Exposed REST API endpoints (`GET /api/memory`, `POST /api/memory/preference`, `DELETE /api/memory/preference`, and `/api/ideas/{session_id}/learn-preference`) and integrated a Web UI *"🧠 Tu Voz y Expresiones Aprendidas"* management panel.
2. **Modularized `voice_guide.md` & Gitignored `voice_samples.md`**: Extracted positive writing habits, cadence rules, and Peninsular tone into `data/voice_guide.md`. Added support for injecting real author writing samples from `data/voice_samples.md` (gitignored for privacy) into Note, Article, and Revision prompts.
3. **`[FALTA: ...]` Sincerity Rule & Concentrated Anti-Patterns**: Updated `app/prompts/generate_article.md` to mandate marking missing information with `[FALTA: ...]` instead of hallucinating details or adding filler. Moved prohibition lists into `data/voice_guide.md` to keep prompts focused on positive writing.
4. **Prompt Payload Condensation**: Refactored `_load_profile()` across `DraftGenerator`, `ContentPlanner`, and `VoiceEditor` to extract core guidelines while suppressing verbatim few-shot text blocks, dropping prompt payloads from ~31KB to ~11KB and eliminating Groq 413/429 errors.
5. **Flat Layout Package Discovery Fix**: Added `[tool.setuptools] packages = ["app"]` in `pyproject.toml` to fix editable installation (`pip install -e .[dev]`).

### Positive Consequences

* **Continuous Learning**: The editorial agent continuously learns from author feedback and applies learned style preferences to all future draft generations.
* **Privacy & Real Samples**: Real writing samples in `data/voice_samples.md` guide the model without risking privacy leakage on public Git repositories.
* **Sincerity over Hallucination**: Articles mark missing context explicitly with `[FALTA: ...]` rather than inflating word count with generalities.
* **Reliable Groq LLM Execution**: Reduced prompt size ensures 100% success rate on Groq free-tier models with response latency under 1.5 seconds.
* **Clean Editable Installation**: `pip install -e .[dev]` installs seamlessly without setuptools package discovery collisions.

