# 0019. Closing Line Echoes the Newsletter's Name, Varied Per Piece

* **Status:** Accepted
* **Date:** 2026-09-28

## Context and Problem Statement

The author wants each piece's closing to include a short line that ties the piece's own content back to the concept behind the newsletter's name ("Fuera de mi cabeza" — getting something out of one's head): examples she gave were phrasings like "sacar[lo] fuera de mi cabeza", "ordenando fuera de mi cabeza", "fuera de mi ordenador", "fuera de mi escritorio". The object varies (cabeza, ordenador, escritorio...) depending on what the piece is actually about.

The risk is obvious given everything else in this project's voice work (ADR 0002, 0011, 0012): if this becomes one fixed sentence repeated at the end of every piece, it turns into exactly the kind of formulaic, ceremonial closing the voice guide already prohibits ("cierres circulares", ADR 0002). The instruction has to produce a varying, content-specific line, not a template.

## Decision Outcome

Added a **"Cierre con eco del nombre"** instruction, worded consistently everywhere it appears:

1. `data/voice_guide.md`: describes the device and explicitly requires varying the object (cabeza / ordenador / escritorio / cuaderno / editor de código / etc.) according to the piece's actual topic, with one bad/good example pair showing a fixed formula versus a topic-specific line.
2. `app/prompts/generate_note.md` and `app/prompts/generate_article.md`: added directly into the existing closing/structure instructions (Note's "Párrafo 3", Article's "Estructura y Ritmo"), explicitly stating it is not a summary or a moral — it's a brief callback, not a formula.
3. `app/prompts/revise_draft.md`: allowed but conditional — a revision may adjust the closing to add or fix this echo only if the author's feedback is actually about the closing, not forced into every revision regardless of what was asked.
4. The `system_prompt` strings in `draft_generator.py` (`generate_note`, `generate_article`): a short reinforcement line, following the same pattern used for the letter tone (ADR 0018).

### Positive Consequences

* Ties every piece back to the newsletter's own identity without becoming a repeated, spottable formula — each closing's specific wording depends on that piece's real content.

### Considered but Not Done

* No literal example closing sentence was hard-coded into any prompt as "the" closing to use — only illustrative, clearly-marked examples, to avoid the model latching onto one phrase and reusing it verbatim across pieces.
