# Changelog

All notable changes to the **Fuera de mi cabeza** personal editorial agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **`app/services/voice_profile.py`**: única función (`load_voice_profile`) que combina `voice_guide.md`, `voice_samples.md` y `editorial_memory.json`. Sustituye seis implementaciones de `_load_profile` que estaban duplicadas o incompletas.
- `VoiceAuditor`, `ArgumentGriller` e `IdeaExplorer` reciben ahora `editorial_memory`, así que el auditor de voz, la entrevista adversarial y el análisis de idea ven las mismas reglas aprendidas que el generador y el editor.

### Fixed
- **Memoria editorial envenenada por síntesis fallida:** cuando la llamada al LLM para sintetizar una regla fallaba, `save_preference_to_profile` guardaba el comentario del autor tal cual (con erratas y a medio cortar) como si fuera una regla limpia. Ahora reintenta una vez y, si no logra una síntesis válida, lanza un error en vez de guardar nada.
- **`editorial_profile.md` se sobrescribía con todo el contexto en cada feedback:** cada corrección volcaba `voice_guide.md` + `voice_samples.md` + `editorial_memory.json` completos dentro de `editorial_profile.md`, duplicando contenido y haciendo crecer el archivo sin control. Ahora solo se le añade la nueva regla en una línea.
- **Deduplicación por similitud, no solo exacta:** `EditorialMemory.add_preference` descartaba únicamente duplicados exactos, así que variantes casi idénticas de la misma regla ("evitar tríos forzados" repetido tres veces con distinta redacción) se acumulaban. Ahora usa una comparación por similitud.
- Limpieza manual, una sola vez, de `data/editorial_memory.json` y `data/editorial_profile.md`: se han consolidado y reescrito las reglas que habían quedado mal formadas o duplicadas.

## [0.5.0] - 2026-09-24

### Added
- **Continuous Editorial Memory (`EditorialMemory`)**: Introduced structured JSON persistence (`data/editorial_memory.json`) capturing author voice preferences across five key dimensions (`favorite_expressions`, `forbidden_words`, `style_rules`, `rhythm_rules`, `opening_styles`).
- **Dedicated Voice Guide & Real Samples (`voice_guide.md` & `voice_samples.md`)**: Modularized voice rules into `data/voice_guide.md` focusing on positive writing habits, rhythm, and Peninsular Spanish tone. Added gitignored `data/voice_samples.md` for real author text samples, automatically injected into Note, Article, and Revision prompts.
- **Personalized Voice Learning REST Endpoints**: Added `/api/memory`, `/api/memory/preference`, `/api/ideas/{session_id}/learn-preference`, and deletion endpoints to capture and manage author feedback continuously.
- **Web UI Memory Management Panel**: Integrated *"🧠 Tu Voz y Expresiones Aprendidas"* panel in `index.html` featuring interactive badge deletion, custom preference input, and auto-learning toggle.

### Changed
- **Article Prompt `[FALTA: ...]` Rule**: Refactored `app/prompts/generate_article.md` to strictly enforce marking missing information or context with `[FALTA: ...]` instead of inventing facts or adding filler text.
- **Concentrated Anti-Pattern Rules**: Moved verbose prohibition lists from individual prompts into `data/voice_guide.md`, allowing prompts to focus on positive writing guidance.
- **65% Prompt Payload Reduction**: Optimized profile loading in `DraftGenerator`, `ContentPlanner`, and `VoiceEditor` to extract core guidelines while stripping verbose verbatim few-shot text blocks, dropping prompt payloads from 31KB to ~11KB and eliminating Groq API 413/429 errors.
- **Enhanced Substack Note Synthesis Prompt**: Refactored `app/prompts/generate_note.md` to strictly enforce 2-3 paragraph articulate note synthesis, natural Peninsular Spanish grammar, and custom opening style adherence.

### Fixed
- **Flat Layout Setuptools Build**: Added `[tool.setuptools] packages = ["app"]` in `pyproject.toml` to fix `pip install -e .[dev]` in flat repository layout.
- **Mock LLM Raw Prompt Echoing**: Fixed `MockLLMClient` topic extraction to prevent verbatim prompt text dumping into generated titles and introductory paragraphs during provider fallback.


## [0.4.1] - 2026-09-22

### Added
- **In-Place Paragraph & Note Revisions**: Added request intent classification (`SPLIT_POST`, `REWRITE_PARAGRAPH`, `INTEGRATE_NOTES`, `GENERAL_REVISION`) in `VoiceEditor` to replace paragraphs in-place and consume bracketed notes `[Nota: ...]` without appending editor metadata footers.
- **Formatted Markdown Tab Preview**: Added dual-tab viewer in Web UI (`index.html`) allowing authors to toggle between a live Substack Markdown preview (`marked.js`) and direct plain text editing.
- **Resilient OmniRoute Lifecycle Management**: Improved `check_omniroute_running` HTTP validation (`status_code < 500`) and added pre-spawn process teardown (`pkill -f omniroute`) to prevent port 20128 collisions.

### Fixed
- **UI Form Control Binding**: Fixed DOM property binding on `<input>` and `<textarea>` elements (`.value` instead of `.innerText`), resolving stuck draft UI state.

## [0.4.0] - 2026-09-21

### Added
- **Native WebM Audio Transcription**: Added full `.webm` and `.mp4` audio file support in `AudioTranscriber` with dynamic MIME type resolution and 30-second HTTP timeouts for Whisper API (Groq / OpenAI).
- **Multi-Tier LLM Fallback Pipeline**: Enabled automatic fallback from local OmniRoute proxy (`http://127.0.0.1:20128`) to direct Groq API (`https://api.groq.com/openai/v1`) using `GROQ_API_KEY`.
- **Dynamic Synthesis in Fallback/Mock Mode**: Implemented multi-marker prompt extraction in `MockLLMClient` to dynamically generate tailored articles, notes, and narrative arcs from raw thoughts and voice notes.
- **Feedback Sanitization & Anti-AI Auditing**: Added feedback input sanitization in `MockLLMClient` to strip pasted audit logs and eliminated banned vocabulary (`clave`, `crucial`, `esencial`) from synthesized responses.
- **Pre-revision Auto-save in UI**: Ensured on-screen `contenteditable` draft edits are saved automatically (`saveDraftChanges`) before requesting LLM revisions.

### Fixed
- Fixed browser audio upload rejection by correctly supplying `audio/webm` content type.
- Fixed static article reproduction in Mock mode by extracting `original_idea` across template marker variations.
- Fixed 500 error in `/api/ideas/{session_id}/explore` by including `narrative_arcs` and `connected_thoughts` in mock responses and prioritizing explore pattern matching.
- Cleaned up header text in `index.html` by removing vendor prefix `(Ruk Lab)`.

## [0.3.0] - 2026-09-17

### Added
- **Adversarial "Grill My Argument" Mode**: Added optional Socratic interrogation interview mode with 3 probing questions before content planning.
- **Inline Draft Editing & Clipboard Copying**: Added direct `contenteditable` draft editing and one-click copy to clipboard in Web UI.
- **Automated Voice Audit**: Added real-time checking for 11 anti-AI writing patterns and Peninsular Spanish cadence rules.
