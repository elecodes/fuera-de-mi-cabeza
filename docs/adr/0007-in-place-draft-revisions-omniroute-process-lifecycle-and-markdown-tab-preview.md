# 0007. In-Place Draft Revisions, OmniRoute Process Lifecycle, and Markdown Tab Preview

* **Status:** Accepted  
* **Date:** 2026-09-22  

## Context and Problem Statement

During interactive draft revision, user feedback (such as requests to rewrite specific paragraphs, split long posts, or integrate bracketed inline notes `[Nota: ...]`) was occasionally being appended as separate metadata sections (e.g. `## Revisión Aplicada`) instead of modifying the draft in-place. Additionally, when starting or checking the OmniRoute local proxy router from the UI, orphan Node supervisor processes on port 20128 caused `EADDRINUSE` port collision errors, and form controls in the Web UI were using `.innerText` instead of `.value`, leading to stale draft displays and unformatted Markdown output.

## Decision Drivers

* **In-Place Revision Integrity**: Ensure paragraph rewrites, post splits, and bracketed notes `[Nota: ...]` modify the draft in-place without adding trailing editor notes or summary footers.
* **Resilient OmniRoute Lifecycle**: Detect broken/crashed local proxy instances (HTTP error status codes) and execute clean process teardowns (`pkill -f omniroute`) prior to spawning new instances.
* **Formatted Substack Preview & Form Control Sync**: Fix form control data binding (`.value`) in Web UI and provide a live **Markdown Tab Preview** ("📖 Vista Previa Formateada" vs "✏️ Editar Texto / Markdown") rendered with `marked.js`.

## Decision Outcome

1. **Intent-Driven Revision Engine (`VoiceEditor`)**: Added `_detect_intent` to classify requests into `SPLIT_POST`, `REWRITE_PARAGRAPH`, `INTEGRATE_NOTES`, and `GENERAL_REVISION`. Updated prompt templates and system prompts in `app/prompts/revise_draft.md` demanding in-place rewriting, regex stripping of inline bracketed notes, and strict prohibition of editor metadata footers.
2. **OmniRoute Process Lifecycle Management (`app/main.py`)**: Updated `check_omniroute_running` to validate HTTP responses (`status_code < 500`) and enhanced `start_omniroute` with pre-spawn process teardown (`pkill -f omniroute` and port 20128 socket cleanup).
3. **Form Control Fix & Markdown Tab Preview (`index.html`)**: Corrected DOM property bindings (`.value` instead of `.innerText`) across all draft inputs/textareas, and added a dual-tab viewer allowing authors to switch between formatted Substack preview (`marked.js`) and direct plain text/Markdown editing.

### Positive Consequences

* **In-place Revisions**: Bracketed notes and specific paragraph rewrites are integrated seamlessly in-place.
* **Reliable OmniRoute Connectivity**: Spurious `EADDRINUSE` collisions and orphan supervisor processes are eliminated.
* **Enhanced Author UX**: Real-time formatted Substack preview with typography, headings, blockquotes, and lists alongside direct Markdown editing.
