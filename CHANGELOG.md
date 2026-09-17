# Changelog

All notable changes to the "Fuera de mi cabeza" Editorial Agent project will be documented in this file.

## [Unreleased]

## [0.4.0] - 2026-09-17

### Added
- **Optional "Grill My Argument" Interview Mode (`ArgumentGriller`):** Added optional adversarial interview service (`app/services/argument_griller.py`) and prompt (`app/prompts/grill_argument.md`) to stress-test premises with 3 deep questions (counter-argument, personal evidence, and limits) before generating long-form article content plans.
- **Grill API Endpoints:** Added `POST /api/ideas/{session_id}/grill` and `POST /api/ideas/{session_id}/grill/answers` in `app/main.py`.
- **Web UI Grill Button & Cards:** Added optional **"🔥 Entrevista Adversarial (Grill My Argument)"** button and interactive card container in `index.html`.
- **Architecture Decision Record (ADR-0005):** Documented optional Grill My Argument mode in `docs/adr/0005-optional-adversarial-grill-my-argument-interview-mode.md`.
- **Unit & Integration Suite (`tests/test_grill_mode.py`):** Added full test suite verifying `ArgumentGriller` service and API endpoints (23/23 tests passing).

## [0.3.1] - 2026-09-17

### Added
- **Archify Living Architecture Diagrams:** Added verified, interactive HTML/SVG architecture diagrams for overall system component mapping (`docs/architecture/archify_architecture.html`) and end-to-end sequence flow (`docs/architecture/archify_sequence_flow.html`).
- **FastAPI Diagram Routes:** Added `/architecture` and `/architecture/sequence` routes in `app/main.py` for direct browser inspection.
- **Automated Diagram Metadata Sync (`scripts/update_diagram_metadata.py`):** Added automation script to dynamically extract current app version (`pyproject.toml`), generation timestamp, and Git commit hash (`git rev-parse --short HEAD`) into diagram headers.
- **Architecture Decision Record (ADR-0004):** Documented Archify living diagrams and metadata automation in `docs/adr/0004-archify-interactive-living-architecture-and-metadata-automation.md`.
- **OmniRoute & OmniRouter Provider Compatibility:** Extended `LLM_PROVIDER` recognition across factory client, main routes, and Web UI status badge.

### Added
- **Multi-Thought & Brain Dump Support:** Enabled raw, multi-fragment text input (notes, bullet points, voice transcripts) in `IdeaInput` and `IdeaExplorer`.
- **Interactive Narrative Arcs (`IdeaExplorer` & Web UI):** Socratic synthesis of 2–3 narrative sequences (`arc-1`, `arc-2`, `arc-3`) with interactive selection cards in `index.html` before content planning (`/api/ideas/{session_id}/select-arc`).
- **Automated Editorial Voice Auditor (`VoiceAuditor`):** Added `VoiceAuditor` service (`app/services/voice_auditor.py`) and prompt (`app/prompts/audit_voice.md`) returning naturalness score (0–100), cadence analysis, and flagged AI anti-patterns (`/api/ideas/{session_id}/audit`).
- **Inline Draft Editing & Auto-Save:** Added `contenteditable="true"` on draft title and body with auto-save endpoint (`/api/ideas/{session_id}/draft/update`).
- **Clipboard Copying:** Added one-click **"📋 Copiar borrador al portapapeles"** button in `index.html`.
- **Memory Preference Storage:** Added `/api/memory/preference` and UI button to store style preferences directly into `data/editorial_memory.json`.
- **Architecture Decision Record (ADR-0003):** Documented interactive narrative arcs, automated voice auditing, and inline draft editing.

### Fixed
- **Revision Title Handling & Frontend Error Safety:** Fixed runtime error when revising drafts without titles or when receiving non-200 responses in `index.html` (`submitRevision`).

## [0.2.2] - 2026-09-15

### Added
- **Architecture Decision Records (`docs/adr/`):** Initialized MADR structure with ADR-0000 (Use MADR), ADR-0001 (Decouple Agent Constitution from Task Prompt Templates), and ADR-0002 (Few-Shot Natural Writing Guidelines and Rhythm/Cadence Rules).
- **Natural Writing & Few-Shot Style Guide (`data/editorial_profile.md`):** Added 5 few-shot example pairs (robotic vs. natural), rhythm/cadence guidelines, preferred vs. avoided connectors, idioms, narrative entry points, and naturalness rules.
- **Prompt Template Enforcement (`app/prompts/`):** Updated `generate_note.md`, `generate_article.md`, and `revise_draft.md` to explicitly enforce few-shot examples and variable sentence rhythm.

## [0.2.1] - 2026-09-14

### Added
- **Agent Constitution (`SOUL.md`):** Added universal agent constitution defining purpose hierarchy, ethical integrity, safety oversight, and behavioral boundaries.

### Fixed
- **OmniRoute Launcher & Status Detection:** Fixed false-positive detection in `/api/system/status` and `/api/system/omniroute/start` by accepting any HTTP response from the OmniRoute endpoint instead of requiring strictly status 200/401. Added non-interactive `npx -y` fallback and polling loop for auto-start reliability.

## [0.2.0] - 2026-09-12

### Added
- **OmniRoute Integration:** Support for local AI gateway/proxy routing (`LLM_PROVIDER=openai-compatible`) with configurable `LLM_BASE_URL`.
- **OmniRoute UI Status & Launcher:** Added live status badge (`🟢 OmniRoute Conectado` / `🔴 OmniRoute Desconectado`) and a one-click **"Start OmniRoute"** button in the header UI (`/api/system/status` & `/api/system/omniroute/start`).
- **SSE Stream Parsing:** Added fallback SSE parser in `OpenAICompatibleClient` to support proxies returning Server-Sent Events stream chunks.

### Changed
- **Anti-AI Writing Rules:** Added 11 strict prohibitions against common AI writing patterns (antitheses, intro abstractions, triad rules, generic metaphors, artificial enthusiasm, circular conclusions, transition questions, em-dash overuse, etc.).
- **Language & Voice Variant:** Switched agent system prompts, editorial profile, and web UI copy (`index.html` subtitle, placeholders, step titles, and alert messages) from Rioplatense voseo to **Español de España (castellano peninsular)** (*Piensa, explora y escribe*, *tú*, *tienes*, *has vivido*).
- **Default Models:** Updated default Groq models in configuration documentation to currently supported models (`openai/gpt-oss-120b`).
