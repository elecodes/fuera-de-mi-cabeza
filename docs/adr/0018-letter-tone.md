# 0018. Letter Tone: Writing to One Reader, Without Letter Formatting

* **Status:** Accepted
* **Date:** 2026-09-28

## Context and Problem Statement

The author wants her writing to feel like a letter — as if the person reading it were reading something addressed to them specifically — without adopting literal letter conventions (a salutation like "Querido lector," or a sign-off like "Un abrazo"). The distinction matters: a fixed greeting/sign-off is a format, easy to imitate mechanically and easy to spot as a formula; what she actually wants is the underlying register — a real, implicit "tú" in mind, the sense of telling one person something rather than publishing to an audience.

## Decision Outcome

Added a **"Tono de carta"** instruction, consistently worded, in four places:

1. `data/voice_guide.md`, under "Cómo Escribo": describes the intent (write as if to a specific person, implicit "tú", no fixed salutation/sign-off) as part of the durable voice definition that flows into every prompt via `load_voice_profile` (ADR 0009).
2. `app/prompts/generate_note.md` and `app/prompts/generate_article.md`: added as an explicit bullet under "Estilo y Voz" / "Tono y Estilo", since instructions phrased as short, explicit list items tend to get followed more literally than a rule buried inside a larger injected block.
3. `app/prompts/revise_draft.md`: same instruction, so a revision doesn't drift away from the letter tone the original draft had.
4. The `system_prompt` strings in `draft_generator.py` (both `generate_note` and `generate_article`) and `voice_editor.py` (`revise`): a short reinforcement line, matching the existing pattern of explicit anti-AI-tic callouts already present there.

Explicitly **not** done: no fixed opening/closing phrases were added anywhere, and no code enforces or checks for a salutation — this is a tone instruction only, not a structural one.

### Positive Consequences

* Reinforced in four places (guide + two generation prompts + revision prompt + system prompts) so the instruction survives condensation/skimming by the model rather than depending on one buried line.

### Considered but Not Done

* A literal letter template (fixed greeting/sign-off) was explicitly rejected by the author — it would read as a formula, the opposite of what she wants.
