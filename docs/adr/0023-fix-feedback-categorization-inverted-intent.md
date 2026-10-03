# 0023. Fix Feedback Categorization: "Stop Using X" Was Being Filed as "Favorite Expression"

* **Status:** Accepted
* **Date:** 2026-10-01

## Context and Problem Statement

The author reported that a note kept including the phrase "una lista de comprobación: evita perder el hilo" even after she had explicitly asked, through the learning feedback flow, to stop using it. Inspecting `data/editorial_memory.json` showed the exact phrase stored under `favorite_expressions` — meaning every prompt was actively being told to *use* it, the opposite of what she asked.

The cause was in `VoiceEditor.save_preference_to_profile`'s category heuristic, which decides where a learned rule gets filed (`favorite_expressions`, `forbidden_words`, `rhythm_rules`, or `style_rules`) based on keyword matches against the author's raw feedback text. The `favorite_expressions` branch was checked first and matched on, among other words, `"usar"`. Since `"no usar"` contains `"usar"` as a substring, feedback like *"no uses esta expresión..."* matched the `favorite_expressions` branch before ever reaching the `forbidden_words` branch (which checked for `"no usar"`, `"evitar"`, etc.) — a request to ban a phrase was silently inverted into a request to favor it. A second, related misfiling was found in the same file: a rule about not forcing three-item lists had also landed in `favorite_expressions` by the same mechanism.

## Decision Outcome

1. **Reordered and tightened the categorization heuristic** in `save_preference_to_profile`: negation/prohibition markers (`"no usar"`, `"no uses"`, `"evitar"`, `"eliminar"`, `"deja de"`, `"ya no"`, etc.) are now checked **first**, before any other category, since inverting a prohibition into a favorite is the worst possible failure mode — far worse than a merely-suboptimal category for a positive instruction. The `favorite_expressions` branch was narrowed to only `"expresión"`, `"muletilla"`, `"giro"` (dropping the overly generic `"usar"`, `"decir"`, and `"frase"` triggers that caused the overlap), and is only reached once negation has already been ruled out.
2. **One-time manual cleanup** of `data/editorial_memory.json` and `data/editorial_profile.md`: removed the misfiled "lista de comprobación" entry (now correctly listed under `forbidden_words`), moved the misfiled three-item-list rule out of `favorite_expressions` (already covered by an existing `rhythm_rules` entry, so simply dropped rather than duplicated), fixed two entries that had been filed under `forbidden_words` as full instructional sentences instead of actual banned words/phrases, and removed duplicate/near-duplicate style and closing-echo rules that had accumulated — the closing-echo instruction is already handled properly, with required variation, by `voice_guide.md` (ADR 0019); a rigid duplicate in `editorial_memory.json` only competed with that more carefully designed version.

### Positive Consequences

* A "stop using this" instruction can no longer be inverted into "use this more" by the categorization logic.
* `data/editorial_memory.json` is back to a small, clean, non-contradictory rule set.

### Considered but Not Done

* Did not change `EditorialMemory.add_preference`'s near-duplicate detection (ADR 0009) — the entries cleaned up here were differently *worded* restatements of similar ideas, not near-identical strings, so the existing similarity-based dedup correctly didn't merge them; catching semantic (not just textual) duplicates would need a different mechanism and is out of scope here.
* Did not add automated detection for future miscategorizations — the reordering fix directly addresses the specific overlap that caused this; broader validation (e.g., flagging when a prohibition-sounding rule lands outside `forbidden_words`) could be a future addition if this recurs in a different form.
