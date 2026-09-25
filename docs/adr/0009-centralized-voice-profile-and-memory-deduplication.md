# 0009. Centralized Voice Profile Loader and Semantic Memory Deduplication

* **Status:** Accepted  
* **Date:** 2026-09-25  

## Context and Problem Statement

Previously, `_load_profile()` was independently implemented across six services (`DraftGenerator`, `VoiceEditor`, `ContentPlanner`, `VoiceAuditor`, `ArgumentGriller`, and `IdeaExplorer`). This duplication led to inconsistent prompt context, as several services (`VoiceAuditor`, `ArgumentGriller`, `IdeaExplorer`) were not injecting active `editorial_memory.json` or `voice_samples.md` rules.

Additionally, failed rule synthesis attempts were occasionally saving raw, truncated user feedback strings directly into `editorial_memory.json`. Furthermore, preference updates were overwriting `editorial_profile.md` by dumping full combined context blocks instead of appending single clean rules, and `EditorialMemory.add_preference()` only filtered exact string matches, allowing near-identical rule variations to accumulate.

## Decision Drivers

* **Single Source of Truth**: Centralize voice profile and memory loading across all services into a single reusable component (`load_voice_profile`).
* **Universal Editorial Context**: Guarantee that audit, interview, and exploration services inherit the exact same voice rules and learned preferences as draft generation and revision.
* **Memory Integrity & Deduplication**: Prevent corrupted synthesis entries and deduplicate near-identical preferences before persisting to `editorial_memory.json`.

## Decision Outcome

1. **Centralized Voice Profile Module (`app/services/voice_profile.py`)**: Created `load_voice_profile()` as a unified loader combining `voice_guide.md`, `voice_samples.md`, and `editorial_memory.json`. Refactored all six services to consume this single loader.
2. **Universal Service Injection**: Injected `EditorialMemory` into `VoiceAuditor`, `ArgumentGriller`, and `IdeaExplorer` so that all editorial pipeline stages share identical author style rules.
3. **Synthesis Validation & Safe Preference Saving**: Updated rule synthesis in `VoiceEditor` to retry failed LLM responses and throw a handled error rather than saving raw, corrupted feedback text.
4. **Semantic Memory Deduplication**: Enhanced `EditorialMemory.add_preference()` to perform normalized similarity checking, preventing near-duplicate rules from accumulating.

### Positive Consequences

* **Unified Editorial Context**: 100% of LLM prompts (analysis, planning, drafting, auditing, revision) operate on identical voice rules and learned memory.
* **Clean Memory Persistence**: Corrupted or raw user feedback strings are rejected before writing to `editorial_memory.json`.
* **Zero Duplication**: Near-identical preference rules are merged seamlessly without inflating memory payloads.
