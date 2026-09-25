# 0012. Concreteness Pairs for Grill My Argument Questions, and Fail-Loud on Invalid Grill Response

* **Status:** Accepted
* **Date:** 2026-09-25

## Context and Problem Statement

`grill_argument.md` ("Grill My Argument") pressure-tests an author's premise before it becomes a long article, through 3 adversarial questions: a counter-argument, a request for personal evidence, and a scope/limit question. Unlike `idea_explorer` (ADR 0011), its job isn't to reconstruct a scene — it's to stress-test the argument itself. But the previous wording for all three questions was abstract enough that both the model's phrasing and the author's answers could stay general ("no estoy de acuerdo", "depende") without being pinned to anything checkable.

Separately, `ArgumentGriller.generate_grill_questions` swallowed any JSON parsing failure and silently returned 3 hardcoded generic fallback questions, the same failure mode already fixed for `VoiceEditor.save_preference_to_profile` in ADR 0009: an LLM failure disguised as a successful, if generic, result.

## Decision Drivers

* **Concreteness tailored to purpose**: unlike `idea_explorer`, not all three questions here should anchor to a lived scene — the counter-argument and scope questions are about the argument's structure, not the author's biography.
* **Consistency**: the same fail-loud principle already applied elsewhere in the pipeline (ADR 0009) should apply here too.

## Decision Outcome

1. **Per-question concreteness, matched to what each question actually tests**:
   - *Counter-argument*: now asks for a specific counter-example or situation where the thesis breaks, not a generic objection.
   - *Personal evidence*: now asks for a real project with an approximate date — the same scene-anchoring approach as `idea_explorer` (ADR 0011), since this question's job genuinely is to extract lived experience.
   - *Scope/limit*: now asks for a specific edge case or category of person/situation, not a general scope statement.
2. **Bad/good example pairs** added for all three, following the same contrastive-example pattern from ADR 0011.
3. **No re-asking rule**: if the idea or arc already names a concrete project or limit, the question should target what's still missing.
4. **`ArgumentGriller.generate_grill_questions` now raises `RuntimeError`** on invalid JSON instead of silently returning fallback questions. The `/api/ideas/{session_id}/grill` endpoint already wrapped this call in a `try/except` returning an HTTP 500 with the error detail, so no endpoint-level change was needed.

### Positive Consequences

* Grill answers should carry the same kind of concrete, checkable material into `content_planner` (which merges `grill_answers` with `user_answers`) as `idea_explorer`'s answers do.
* A broken Grill response now surfaces as a visible error instead of silently degrading to generic, unhelpful questions.

### Considered but Not Done

* Kept the JSON output format for this prompt (a 3-item string array), consistent with ADR 0010: this is genuinely small structured data, not a prose block.
