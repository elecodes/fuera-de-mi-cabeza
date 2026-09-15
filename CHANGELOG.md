# Changelog

All notable changes to the "Fuera de mi cabeza" Editorial Agent project will be documented in this file.

## [Unreleased]

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
