# 0010. Plain-Text LLM Output for Note, Article, and Revision Generation

* **Status:** Accepted
* **Date:** 2026-09-25

## Context and Problem Statement

`DraftGenerator.generate_note`, `DraftGenerator.generate_article`, and `VoiceEditor.revise` all asked the LLM to return the entire draft wrapped in a JSON object, with the prose itself embedded as a single escaped string (`{"format": ..., "title": ..., "content": "..."}`). This had two costs:

1. **Fragility**: any unescaped quote, newline, or control character inside the generated prose could break `json.loads()` parsing, especially for longer articles.
2. **Voice quality**: writing prose that must simultaneously be valid, escaped JSON pushes the model to attend to formatting mechanics rather than to voice, rhythm, and content — the opposite of what this project is trying to achieve.

Separately, `VoiceEditor.revise` asked the model to return `title` and `format` alongside the revised content. If the model returned a non-empty `title`, the code silently overwrote the draft's actual title (`if "title" not in data or not data["title"]: data["title"] = current_draft.title`), even when the author never asked to rename the piece.

## Decision Drivers

* **Prose quality over formatting compliance**: the model should be free to write natural prose without worrying about JSON escaping.
* **Robustness**: no output should silently corrupt the draft because of a stray quote or newline.
* **Least surprise**: revising a draft's content should never rename it unless explicitly asked.

## Decision Outcome

1. **Plain text for Note and Revision**: the LLM returns the content directly, no envelope. `app/services/text_output.py::strip_code_fences` strips an accidental Markdown code fence if the model wraps its answer in one despite instructions.
2. **Title/content markers for Article**: the LLM returns `===TITULO===\n<title>\n===CONTENIDO===\n<content>`, parsed by `app/services/text_output.py::parse_titled_content`. If the model omits the markers, the whole response is treated as content and the previously chosen title is kept.
3. **Revision never sets the title or format**: `VoiceEditor.revise` no longer asks the model for `title`/`format` at all. Both are always inherited from `current_draft`, closing the silent-rename gap described above.
4. **Structured stages keep JSON**: `content_planner`, `idea_explorer`, `voice_auditor`, and `argument_griller` continue to return JSON, since their output is genuinely multi-field (arrays of options, key points, scored issues) rather than one long prose block.
5. **Removed a duplicated memory injection**: while touching these system prompts, we found `editorial_memory.get_context()` was being called a second time directly inside the `system_prompt` construction, even though it was already included in `editorial_profile` via `load_voice_profile` (ADR 0009). The duplicate call was removed.

### Positive Consequences

* No more JSON-escaping failures on long or quote-heavy drafts.
* Revisions can no longer silently rename a draft.
* Slightly smaller prompts (one less duplicated memory block per call).

### Negative Consequences

* Article generation now depends on the model reliably emitting two literal markers instead of a JSON key; `parse_titled_content` degrades gracefully (falls back to the previously chosen title) if it doesn't, but a provider that ignores instructions entirely could produce a title-less article.
