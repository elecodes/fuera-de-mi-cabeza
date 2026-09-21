# 0006. WebM Audio Transcription and Resilient Multi-Tier LLM Fallback Pipeline

* **Status:** Accepted  
* **Date:** 2026-09-21  

## Context and Problem Statement

During voice recording in modern web browsers, audio blobs are captured in `.webm` format. Previously, the transcription service hardcoded MIME types to `audio/mpeg` and had a tight 5-second HTTP timeout, causing transcription failures or silent fallback triggers. Furthermore, when local proxy routers (OmniRoute) were unavailable or remote API keys returned errors, the LLM client fell back to static mock responses that did not synthesize dynamic user feedback, raw voice notes, or anti-AI style constraints.

## Decision Drivers

* **Native Browser Voice Recording**: Support `.webm` and dynamic MIME types with extended timeouts for Whisper transcription (Groq / OpenAI).
* **Resilient LLM Routing**: Seamless multi-tier fallback: OmniRoute local proxy → Direct Groq API → Dynamic MockLLMClient synthesis.
* **Dynamic Mock Synthesis**: Ensure fallback mode parses raw thoughts, voice notes, and revision feedback to generate clean, fluid prose in Castellano Peninsular without anti-AI banned vocabulary (`clave`, `crucial`, etc.) or raw string interpolation.

## Decision Outcome

1. **Audio Transcriber (`AudioTranscriber`)**: Added native `.webm` and `.mp4` support, dynamic MIME type detection, 30s HTTP timeout, and flexible provider routing in `app/services/audio_transcriber.py`.
2. **Multi-Tier Provider Fallback (`OpenAICompatibleClient`)**: Added automatic fallback to direct Groq API (`https://api.groq.com/openai/v1`) when local OmniRoute proxy connections fail.
3. **Dynamic Synthesis in Mock (`MockLLMClient`)**: Replaced static string templates with dynamic extraction of user ideas, voice notes, and revision feedback. Added feedback sanitization to strip raw audit logs and enforced strict compliance with `data/editorial_profile.md` anti-AI style rules.
4. **UI Integration (`index.html`)**: Added pre-revision auto-save (`saveDraftChanges`) to preserve on-screen edits before revision requests and cleaned up UI component header text.

### Positive Consequences

* **Robust Offline & Online Editing**: Draft generation and revisions work reliably across direct cloud APIs, local proxies, and mock fallback modes.
* **Seamless Audio Workflows**: Native voice notes recorded in browser are transcribed and incorporated into the editorial pipeline without mime-type rejection.
