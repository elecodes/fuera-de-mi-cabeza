# 0011. Scene-Anchored Socratic Questions in Idea Explorer

* **Status:** Accepted
* **Date:** 2026-09-25

## Context and Problem Statement

`IdeaExplorer.analyze` asks the LLM to generate 2-3 Socratic questions meant to surface the author's real, lived experience behind an idea, so later drafting stages have concrete material to work with instead of generalities. The previous prompt asked for "el evento o fricción concreta" in the abstract (e.g., "¿Qué hecho o conversación concreta de esta semana detonó esta reflexión?"). In practice, this framing was specific enough to sound targeted but still left room for the model — and the author answering it — to respond with a general topic or feeling rather than an actual, checkable detail (a moment, a place, an exact phrase, a number).

Since drafts are explicitly forbidden from inventing experiences the author hasn't shared (see `voice_guide.md` and the "REGLA FUNDAMENTAL" in each prompt), the quality of the author's answers to these questions is the main lever available for making drafts sound concrete and personal instead of generic.

## Decision Drivers

* **Concreteness over topic-matching**: a question should be unanswerable with a vague or general statement.
* **Avoid redundant questions**: if the author's original idea already contains a concrete detail, the question should probe for what's still missing, not repeat what's already known.
* **Prompt reliability**: contrastive examples (bad vs. good question) are a more reliable steering mechanism for LLMs than an abstract instruction alone.

## Decision Outcome

1. **Concreteness test added to the prompt**: before including a question, the prompt now instructs the model to check whether the question could be answered with a general idea, opinion, or vague feeling ("me sentí frustrada"); if so, it must be rewritten until the only possible answer is a concrete fact (a moment, a place, an approximate date, a name, a number, an exact quote, a tool, a physical action).
2. **The three question types were redefined around a scene, not a theme**:
   - *Scene of the trigger*: what the author was doing right before, where, with whom.
   - *The exact detail that caused the friction*: an exact phrase, a message, a concrete error, a number.
   - *The concrete action that followed*: what the author literally did (or stopped doing) next, not an abstract lesson.
3. **Bad/good example pairs** were added for each of the three question types, to give the model a contrastive anchor rather than only a declarative instruction.
4. **No re-asking rule**: if the author's original idea already states a date, a name, a tool, or a direct quote, the question must not ask for it again — it should target what's still missing.
5. `MockLLMClient`'s default example questions were updated to the same style, so local development without an API key stays representative of the real prompt's behavior.

### Positive Consequences

* Author answers should carry more usable, concrete material into `draft_generator`, which already reuses answers close to verbatim.
* Reduces the odds of asking the author to repeat something they already wrote.

### Considered but Not Done

* `grill_argument.md` (the adversarial "Grill My Argument" interview) has a different purpose — pressure-testing the argument's premise, not extracting scene detail — and its "Evidencia Personal" question already asks for "un momento o proyecto específico". The same bad/good example-pair pattern could be applied there if its answers turn out to be too generic in practice, but this was left out of scope for this change.
