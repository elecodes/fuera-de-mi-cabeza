# 0005. Optional Adversarial "Grill My Argument" Interview Mode

* **Status:** Accepted  
* **Date:** 2026-09-17  

## Context and Problem Statement

When authors write long-form essays or deep Substack Posts, simple Socratic questions may not provide enough pressure to uncover hidden assumptions, counter-arguments, or missing personal evidence. However, forcing an intensive interrogation loop for quick Substack Notes introduces unnecessary friction. We need an optional, high-depth "Grill My Argument" interview mode that authors can trigger on-demand before content planning.

## Decision Drivers

* **Optional Depth Toggle**: Keep standard note planning fast (low friction) while offering deep interrogation for articles.
* **Adversarial Questioning**: Generate 3 specific probing questions: counter-argument challenge, personal evidence requirement, and boundary/audience limit.
* **Planner Integration**: Seamlessly feed adversarial answers into `ContentPlanner` to refine key points and opening direction.

## Decision Outcome

1. **Model Extension (`EditorialSession`)**: Added `grill_mode`, `grill_questions`, and `grill_answers` to `app/models/session.py`.
2. **Service & Prompt (`ArgumentGriller` & `app/prompts/grill_argument.md`)**: Service generating 3 adversarial questions based on the selected narrative arc and original brain dump.
3. **Endpoints**: Added `POST /api/ideas/{session_id}/grill` and `POST /api/ideas/{session_id}/grill/answers` in `app/main.py`.
4. **Web UI (`index.html`)**: Added optional **"🔥 Entrevista Adversarial (Grill My Argument)"** button in Step 2 with interactive question cards.
5. **Testing**: Comprehensive unit and integration coverage in `tests/test_grill_mode.py`.

### Positive Consequences

* **Deep Article Rigor**: Gives authors an on-demand devil's advocate to stress-test their arguments before writing.
* **Zero Friction for Quick Notes**: Default note creation flow remains instant and uninhibited.
