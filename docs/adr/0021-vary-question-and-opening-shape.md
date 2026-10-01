# 0021. Vary Question 1's Angle and the Opening Sentence Shape

* **Status:** Accepted
* **Date:** 2026-10-01

## Context and Problem Statement

The author reported that new Notes felt too similar to her previously published pieces — not generic AI writing, but specifically repeating a sentence-level pattern. Comparing a new draft's opening ("Ayer, mientras leía el borrador que la IA había tirado, me di cuenta de que...") against an earlier published Note's opening ("El otro día, mientras intentaba redactar el primer post en Substack, me quedé sin saber cómo seguir...") showed an identical grammatical skeleton: *"[marcador temporal], mientras [gerundio], me [verbo de darse cuenta]..."*.

The cause traced back to `idea_explorer`'s "Pregunta 1 (Escena del detonante)" (ADR 0011), which always asks a fixed-shape question: "¿Qué estabas haciendo justo antes de que se te ocurriera esto?". Since `draft_generator` is deliberately designed to reuse the author's answers close to verbatim (the entire point of ADR 0011's scene-anchoring work — concreteness over invented generalities), a fixed question shape produces answers with a fixed grammatical shape, and those answers becoming the literal opening sentence meant every piece opened with the same mechanical frame. The scene-anchoring work that made each piece's *content* more concrete was, as an unintended side effect, making every piece's *opening sentence structure* identical.

## Decision Outcome

Two changes, addressing both ends of the pipeline:

1. **`app/prompts/explore_idea.md` — Pregunta 1 now rotates its angle** instead of always asking "¿qué estabas haciendo justo antes?". Four alternative framings were added (the place and action, an external trigger, the exact phrase in mind, the object/tool in front of her), with an explicit instruction to pick whichever fits the specific idea rather than defaulting to the same one every time — plus a bad/good example pair where "bad" is now defined as *reusing the same question verbatim across explorations*, not just a vague question (the earlier failure mode from ADR 0011).
2. **`app/prompts/generate_note.md` and `app/prompts/generate_article.md`** (and the matching `system_prompt` strings in `draft_generator.py`) now explicitly instruct: don't reuse the "[time marker], mientras [gerund], me di cuenta de..." skeleton as the literal opening sentence. If the author's scene answer has that shape, rewrite it, reorder it, or open from a different point (the reflection, the friction detail, the object) and place the scene a little later in the paragraph instead.

### Positive Consequences

* Keeps the concreteness gains from ADR 0011 (the answers are still anchored to a real, specific moment) while removing the mechanical, repeated sentence-level template that concreteness had accidentally produced.

### Considered but Not Done

* Did not remove or weaken the "reuse the author's answers near-verbatim" instruction itself — that's the right design for authenticity (ADR 0010/0011). The fix targets *where and how* the scene answer lands in the final sentence, not whether it gets used at all.
* Did not touch `voice_samples.md` or the voice-learning memory — initial suspicion was that past sample text was leaking into generation, but `KnowledgeBase`/RAG (ADR 0020) was confirmed to never touch generation prompts, and the structural match was traced precisely to the question-shape → answer-shape → opening-shape chain described above, not to sample reuse.
