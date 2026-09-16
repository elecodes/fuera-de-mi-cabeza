# 0003. Interactive Narrative Arcs, Automated Voice Auditing, and Inline Draft Editing

* **Status:** Accepted  
* **Date:** 2026-09-16  

## Context and Problem Statement

Authors often start writing with scattered thoughts, bullet points, or voice note fragments rather than a single polished idea. Furthermore, transitioning directly from raw thoughts to a draft can feel opaque, and authors need a way to choose how their ideas are ordered and connected before generating content. Lastly, authors require the flexibility to edit drafts directly in the notebook UI, copy them to clipboard, and audit the naturalness of their text against anti-AI rules.

## Decision Drivers

* **Multi-Thought Ingestion**: Support freeform brain dumps, bulleted notes, and multi-fragment thoughts.
* **Socratic Thought Ordering**: Present 2–3 alternative **Narrative Arcs** to let the author steer the logical flow before content planning.
* **Substack Format Strategy**: Explicit separation between Substack Notes (short discovery posts) and Substack Posts (deep-dive articles).
* **Automated Voice Auditing**: Evaluate candidate draft text against the 11 strict anti-AI rules and cadence guidelines in `data/editorial_profile.md`.
* **Author Agency & Direct Editing**: Allow authors to edit text directly inline in the notebook view (`contenteditable`) and copy final drafts to clipboard with one click.

## Decision Outcome

We upgraded the personal editorial agent pipeline and Web UI:
1. **Multi-Input Ingestion & Narrative Arc Synthesizer (`IdeaExplorer`)**: Updated models (`IdeaInput`, `IdeaAnalysis`, `NarrativeArc`) and prompts to extract core themes, identify connected thoughts, and generate 2–3 narrative sequences (`arc-1`, `arc-2`, `arc-3`).
2. **Interactive Guidance Cards (Web UI)**: Integrated an interactive narrative arc selector into `index.html` allowing the user to pick an ordering before advancing to the plan.
3. **Automated Voice Auditor (`VoiceAuditor`)**: Added `VoiceAuditor` service (`app/services/voice_auditor.py`) and prompt (`app/prompts/audit_voice.md`) returning a 0–100 score, cadence analysis, and flagged AI anti-patterns (`/api/ideas/{session_id}/audit`).
4. **Inline Draft Editing & Clipboard Copying**: Enabled `contenteditable="true"` on draft title and body, connected live auto-saving (`/api/ideas/{session_id}/draft/update`), and added a one-click clipboard copy button.
5. **Memory Preference Storage**: Added `/api/memory/preference` to persist style rules into `data/editorial_memory.json`.

### Positive Consequences

* **Flexible Thought Structuring**: Authors can start with raw bullet points and decide how they link together.
* **Full Author Control**: Inline editing ensures the author remains in full control of every word without forcing LLM regeneration for minor tweaks.
* **Instant Style Feedback**: The voice audit tool gives objective feedback against AI clichés and sentence monotony.

### Negative Consequences

* Additional API endpoints and UI state management required for narrative arcs and draft auto-saving.
