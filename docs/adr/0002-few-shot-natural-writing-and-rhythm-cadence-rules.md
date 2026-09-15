# 0002. Few-Shot Natural Writing Guidelines and Rhythm/Cadence Rules

* **Status:** Accepted  
* **Date:** 2026-09-15  

## Context and Problem Statement

LLM generation tends to default to robotic, template-driven Spanish output characterized by uniform sentence lengths, academic/corporate connectors (*asimismo*, *por consiguiente*, *no obstante*), passive phrasing, and artificial introductions (*En un mundo donde...*). 

We needed a systematic, reproducible way to enforce a natural, human, conversational writing style in Peninsular Spanish (*Español de España*) across all generated notes, articles, and revisions without compromising fidelity to the author's core ideas.

## Decision Drivers

* **Output Naturalness**: Texts must sound authentic, spontaneous, and human-written rather than AI-generated.
* **Concrete Guidance vs. Abstract Adjectives**: Generic tone descriptors like "reflexivo" or "humano" do not effectively steer LLM output; concrete few-shot comparisons and specific grammatical habits are required.
* **Cadence & Rhythm**: Sentence structure must vary (combining short punchy statements with longer reflective thoughts) to break robotic monotony.
* **Preferred Connectors**: Conversations require natural Spanish connectors (*pero*, *así que*, *por eso*, *en realidad*, *el caso es que*, *en la práctica*, *sobre el papel*).

## Decision Outcome

We embedded a comprehensive **Guía de Estilo y Hábitos de Escritura Natural** directly inside `data/editorial_profile.md` and updated all task prompt templates (`generate_note.md`, `generate_article.md`, `revise_draft.md`) to explicitly enforce it.

Key components added:
1. **5 Few-Shot Example Pairs** contrasting robotic vs. natural writing across 5 common narrative situations (introducing an idea, explaining something, expressing uncertainty, describing an experience, giving an opinion).
2. **Rhythm and Cadence Rules**: Requiring varied sentence lengths and spontaneous structural flow (`frase corta → desarrollo → frase más larga con matices → conclusión breve`).
3. **Preferred vs. Avoided Connectors**: Explicit whitelist of natural connectors and blacklist of academic/corporate transitions.
4. **Permitted vs. Avoided Idioms**: Guidelines on natural expressions vs. artificial buzzwords.
5. **Concrete Narrative Entry Points**: Prioritizing concrete observations over broad abstract introductions.
6. **Core Naturalness Rule**: Directing naturalness to emerge from rhythm, concrete entry points, and reasoning matices rather than forced slang.

### Positive Consequences

* **Drastic Improvement in Output Tone**: LLM outputs adopt a realistic human cadence and conversational flow.
* **Unified Enforcement**: Because `{editorial_profile}` is interpolated across all prompts, every agent stage (exploration, drafting, revision) automatically inherits the few-shot rules.
* **Zero Inventory / Hallucination**: Naturalness rules operate purely on syntax, cadence, and tone without encouraging the LLM to invent fictive anecdotes or facts.

### Negative Consequences

* Increased prompt token count per LLM request due to few-shot examples and connector lists.
