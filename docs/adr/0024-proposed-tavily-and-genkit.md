# 0024. Proposed: Tavily (Fact Verification) and Genkit (Orchestration) — Not Implemented

* **Status:** Proposed (informational only — nothing in this ADR has been built)
* **Date:** 2026-10-03

## Context

Two ideas were discussed for possible future work: integrating [Tavily](https://www.tavily.com) (a web-search API built for LLM/agent use) and [Genkit](https://genkit.dev) (Google's multi-language AI orchestration framework). Both were explicitly requested to be captured as reference material for a future decision, not acted on now.

## Tavily (web search)

**What it is**: a search API that returns results pre-cleaned for LLM consumption, with a free tier (1,000 credits/month, no card required as of the time of writing) — fits the project's existing pattern of favoring free-tier APIs (Gemini embeddings, ADR 0020).

**Where it could genuinely help**:
- **Fact verification, not generation.** The project's core rule is never to invent — if a draft states something factual (a model name, a date, "this just launched"), Tavily could check it's still accurate, especially given how fast the author's subject matter (AI, tooling) moves. This would work like the existing `[FALTA: ...]` convention in `generate_article.md` (flagging missing context) but for factual accuracy — flag, don't silently correct or embellish.
- **Voice auditing, not content**: as a secondary idea, checking whether a phrase that reads as "canned" is in fact a widely-used cliché online, as an extra signal alongside the existing fixed antipattern list.

**Where it does NOT fit**: as a source of content or inspiration fed into generation. The project's voice work (letter tone, ADR 0018; banned invented metaphors, ADR 0022; no inventing experiences) is specifically about personal, lived, idiosyncratic writing — piping web search results into the generation prompt is close to the opposite of that, and risks diluting the voice with generic web content. If ever used for linking to external sources in an article, the same pattern as the RAG feature (ADR 0020) should apply: surfaced to the author as something she sees and chooses to use, never injected into the model's prompt automatically.

**If pursued later**: scope it narrowly — a manual, opt-in verification step (like the Drive export button, not automatic), that only flags uncertain claims, never rewrites or adds text on its own. A natural home would be alongside the existing voice-audit flow (`🔍 Auditar Voz Editorial`).

## Genkit (agent orchestration)

**What it is**: Google's open-source framework for building AI features — flow orchestration, prompt management, tool calling, RAG helpers, model-agnostic plugins, and a local dev UI for tracing/debugging.

**Why it doesn't fit well here, for now**:
- **Python SDK maturity**: as of early 2026, Genkit's Python SDK is still Alpha (v0.11.0), explicitly pre-1.0 with breaking changes possible between releases. JavaScript/TypeScript and Go are production-ready; Python — this project's entire stack — is not. Taking a dependency on an Alpha SDK cuts directly against the stability and fail-loud principles this project has deliberately built toward (ADR 0009, 0012, 0013).
- **Redundant with what already exists and is tailored to this project**: flow orchestration (the `idea_explorer → content_planner → draft_generator → voice_auditor/voice_editor` pipeline), provider abstraction (`LLMClient` + `MockLLMClient`/`OpenAICompatibleClient`, with the Groq fallback chain and mock mode), and RAG (`KnowledgeBase`, ADR 0020) are all already built, tested (103+ tests), and shaped exactly around this project's actual needs. Replacing them with generic framework equivalents would mean rebuilding working, well-understood code for a framework's abstractions instead of this project's own.
- **Tool-calling abstraction isn't needed**: this app's pipeline is a linear, explicit chain of steps, not an agent dynamically deciding which tool to invoke — Genkit's tool-calling story solves a problem this project doesn't have.
- **Tooling footprint**: Genkit's CLI and dev UI have historically been Node.js-based even for non-JS SDKs, which would introduce a Node toolchain dependency into an otherwise pure-Python project just for developer tooling.

**The one genuine gap it would fill**: observability — a UI to inspect each pipeline step's prompt and response during development. This has been done manually throughout this project's development (reading prompt files and system strings by hand to diagnose voice issues). It's a real, recurring friction point.

**Recommendation if that specific need becomes pressing**: solve observability directly and cheaply — structured logging of each pipeline step's input/output (prompt sent, raw response, parsed result) — rather than adopting a whole Alpha-stage orchestration framework for one feature. Revisit Genkit itself only once its Python SDK reaches a stable 1.0 release.

## Decision

Neither is being implemented now. This ADR exists purely as a reference for a future decision.
