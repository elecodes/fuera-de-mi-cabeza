# 0004. Archify Interactive Living Architecture & Metadata Automation

* **Status:** Accepted  
* **Date:** 2026-09-17  

## Context and Problem Statement

As the codebase grows, static documentation and architecture diagrams often suffer from "zombie documentation"—where diagrams become outdated and developers cannot verify whether a diagram reflects the current system state or a version from months prior. We need verifiable, interactive architectural documentation (component diagrams and sequence flows) and an automated mechanism to keep version, timestamp, and Git commit metadata synchronized.

## Decision Drivers

* **Verifiable Architecture Representation**: Use Archify IR (JSON Intermediate Representation + interactive HTML) to render verified component and sequence diagrams without LLM hallucination.
* **Interactive Visualization**: Provide dark/light theme toggling, component path tracing, and step-by-step sequence inspection.
* **Living Documentation Access**: Serve architecture diagrams directly via FastAPI web routes (`/architecture` and `/architecture/sequence`).
* **Automated Metadata Versioning**: Automatically tag every diagram with current app version (`v0.3.0`), generation date, and Git commit hash (`git rev-parse --short HEAD`).

## Decision Outcome

We implemented Archify interactive diagrams and an automated metadata sync workflow:
1. **Component Architecture Diagram (`docs/architecture/archify_architecture.html`)**: Interactive diagram mapping Web UI, FastAPI Backend, Domain Services (`IdeaExplorer`, `VoiceAuditor`, etc.), LLM Layer (`OmniRoute` & Groq), and Storage.
2. **Sequence Flow Diagram (`docs/architecture/archify_sequence_flow.html`)**: Step-by-step interactive breakdown of the complete editorial lifecycle (Brain Dump ➔ Narrative Arcs ➔ Content Plan ➔ Draft ➔ Voice Audit ➔ Revision).
3. **FastAPI Routes**: Added `/architecture` and `/architecture/sequence` routes in `app/main.py`.
4. **Metadata Sync Automation Script (`scripts/update_diagram_metadata.py`)**: Script that extracts Git commit, app version (`pyproject.toml`), and current date to update diagram headers automatically.
5. **Test Integration**: Integrated metadata and diagram route verification into the `pytest` test suite (`tests/test_api.py`).

### Positive Consequences

* **Living & Verifiable System Map**: Architectural changes are visual, interactive, and grounded in exact code paths.
* **Zero-Stale Metadata**: Automated metadata updates guarantee every diagram explicitly states its exact Git commit hash, app version, and timestamp.
* **Dual Access**: Diagrams can be viewed via local dev server (`http://localhost:8000/architecture`) or downloaded as standalone HTML.
