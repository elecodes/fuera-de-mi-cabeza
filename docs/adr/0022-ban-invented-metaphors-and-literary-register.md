# 0022. Ban Invented Metaphors/Similes and Elevated Literary Register

* **Status:** Accepted
* **Date:** 2026-10-01

## Context and Problem Statement

The author reported that generated Notes didn't sound natural or colloquial, even after giving explicit feedback to make a draft "más coloquial, más natural" through the revision flow. A concrete example she flagged:

> "sonaba como una máquina que recita datos sin respirar... como si una capa de polvo hubiera cubierto el papel que habitualmente pulso con la mano."

Checking this against the existing voice rules (ADR 0002 and others) showed a real gap: `voice_guide.md`'s "Qué Evitar" section only banned **known, clichéd** AI metaphors (e.g., "brújula, no mapa") and corporate-style inflated adjectives (*crucial*, *esencial*). It had no rule against the model **inventing a brand-new, original metaphor or simile** for the occasion — which isn't a recognizable cliché, so the existing filter never caught it, but still reads as ornate, literary-essay prose rather than her actual spoken, direct voice. The same gap existed for vocabulary: the "adjetivos inflados" list named specific corporate buzzwords, but had nothing against **elevated literary/essayistic vocabulary** (*desencadenó*, *se diluyó*, *escasa*, *pulso* as a verb for writing, *al fin*) that isn't corporate jargon but is still far more formal than how she actually talks.

This explains why revision feedback alone didn't fix it: `revise_draft.md` told the model to apply feedback according to the voice guide, but the voice guide itself didn't define what "more colloquial" concretely meant — so "más coloquial" had no specific, checkable target to revise toward.

## Decision Outcome

1. **`data/voice_guide.md`**: added two new, explicit bans under "Qué Evitar":
   - *Metáforas y símiles inventados para la ocasión* — not just clichéd ones. The author's own flagged examples are used verbatim as the "don't do this" case, since a concrete real counter-example teaches this far more precisely than an abstract rule.
   - *Vocabulario de registro literario o ensayístico* — a small list of elevated words paired with their plain, spoken Spanish equivalent (*desencadenó → pasó/empezó*, *se diluyó → se perdió*, etc.).
2. **`app/prompts/generate_note.md` and `generate_article.md`**: added the same two bans directly in the style instructions, so new drafts avoid this from the start rather than relying on a revision pass to catch it.
3. **`app/prompts/revise_draft.md`**: added an explicit rule for when feedback uses words like "más coloquial", "más natural", or "que suene menos a IA" — check specifically for invented metaphors and elevated vocabulary first, since those are now understood to be the most common concrete cause of that complaint.
4. **`system_prompt` strings in `draft_generator.py` and `voice_editor.py`**: extended the existing banned-tics line (which already named "metáforas trilladas") to also explicitly forbid invented ones and literary-register vocabulary, with the same word examples, so the instruction survives even if the model skims past the fuller guide text.

### Positive Consequences

* "More colloquial/natural" feedback now maps to two specific, checkable things to fix, instead of an abstract instruction the model has no concrete target for.
* The ban is anchored to the author's own real examples, which is a stronger and more precise teaching signal than a generic rule.

### Considered but Not Done

* Did not touch `idea_explorer`'s questions or `draft_generator`'s answer-reuse logic (ADR 0021) — this is a separate problem (register/vocabulary, not structural repetition) and needed its own fix.
