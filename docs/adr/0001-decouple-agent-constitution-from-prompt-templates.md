# 0001. Decouple Agent Constitution (`SOUL.md`) from Task Prompt Templates

* **Status:** Accepted  
* **Date:** 2026-09-15  

## Context and Problem Statement

The application uses LLM agents to explore ideas (`idea_explorer`), generate content plans (`content_planner`), draft notes and articles (`draft_generator`), and revise text (`voice_editor`). 

To govern agent behavior, we introduced a universal agent constitution (`SOUL.md`). We needed to decide how `SOUL.md` interacts with individual task prompts (`app/prompts/*.md`) and the author's voice profile (`data/editorial_profile.md`).

## Decision Drivers

* **Prompt Efficiency & Token Cost**: Passing a 190-line universal constitution in every LLM call adds significant token overhead and latency.
* **Separation of Concerns**: Macro-level ethics and safety governance (`SOUL.md`) operate at a different layer than task-specific generation directives (`app/prompts/`) and author style guidelines (`data/editorial_profile.md`).
* **Maintainability & Modularity**: Changing author voice or prompt formatting should not require altering macro-governance documents.

## Considered Options

1. **Direct Injection**: Read `SOUL.md` at runtime in Python services and inject it into every `system_prompt`.
2. **Decoupled Architecture**: Keep `SOUL.md` as an overarching behavioral spec and design contract for developers/AI agents, while driving runtime LLM behavior through modular prompt templates (`app/prompts/`) and the editorial profile (`data/editorial_profile.md`).

## Decision Outcome

Chosen option: **Decoupled Architecture** (Option 2).

`SOUL.md` serves as a macro-level constitution and design contract. Task execution, output structure, anti-AI pattern prohibitions, and author voice are specified directly in `app/prompts/` and `data/editorial_profile.md`.

### Positive Consequences

* **Lower Latency & Token Usage**: LLM requests remain lean and targeted.
* **Clarity of Purpose**: Prompt templates focus strictly on output quality and formatting; `SOUL.md` focuses on system ethics, principal hierarchy, and tool safety.
* **Easier Fine-Tuning**: Tone, cadence, and few-shot examples can be updated in `app/prompts/` without touching macro governance.

### Negative Consequences

* If specific macro-safety rules from `SOUL.md` are needed at runtime for specialized agents, they must be explicitly mirrored or referenced in prompt templates.
