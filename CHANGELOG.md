# Changelog

All notable changes to the **Fuera de mi cabeza** personal editorial agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
