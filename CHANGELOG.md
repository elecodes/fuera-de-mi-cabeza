# Changelog

All notable changes to the "Fuera de mi cabeza" Editorial Agent project will be documented in this file.

## [0.2.0] - 2026-09-12

### Added
- **OmniRoute Integration:** Support for local AI gateway/proxy routing (`LLM_PROVIDER=openai-compatible`) with configurable `LLM_BASE_URL`.
- **SSE Stream Parsing:** Added fallback SSE parser in `OpenAICompatibleClient` to support proxies returning Server-Sent Events stream chunks.

### Changed
- **Anti-AI Writing Rules:** Added 11 strict prohibitions against common AI writing patterns (antitheses, intro abstractions, triad rules, generic metaphors, artificial enthusiasm, circular conclusions, transition questions, em-dash overuse, etc.).
- **Language & Voice Variant:** Switched agent system prompts and editorial profile from Rioplatense voseo to **Español de España (castellano peninsular)** (*tú*, *tienes*, *has vivido*).
- **Default Models:** Updated default Groq models in configuration documentation to currently supported models (`openai/gpt-oss-120b`).
