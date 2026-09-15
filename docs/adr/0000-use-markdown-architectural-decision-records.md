# 0000. Use Markdown Architectural Decision Records (MADR)

* **Status:** Accepted  
* **Date:** 2026-09-15  

## Context and Problem Statement

As the "Fuera de mi cabeza" project evolves—introducing multi-agent pipelines, prompt engineering patterns, LLM provider routing, and editorial constitutions—we need a lightweight, structured way to document key architectural decisions, their rationale, and their tradeoffs for human collaborators and AI assistants.

## Decision Drivers

* Need for persistent, version-controlled architectural context alongside code.
* Clear distinction between *what* changed (recorded in `CHANGELOG.md`) and *why* it changed (recorded in ADRs).
* Simple, human-readable markdown format compatible with git workflows.

## Considered Options

1. **Markdown Architectural Decision Records (MADR)**
2. **Wiki or external documentation system (Notion/Confluence)**
3. **Inline code comments and pull request descriptions**

## Decision Outcome

Chosen option: **Markdown Architectural Decision Records (MADR)** stored directly in `docs/adr/`.

### Positive Consequences

* Architectural decisions remain collocated with source code.
* AI agents and human developers can read architectural context directly from the repository.
* Easy to review in pull requests and maintain via git history.

### Negative Consequences

* Requires discipline to create and maintain records as major technical decisions are made.
