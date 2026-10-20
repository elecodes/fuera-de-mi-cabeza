# 0026. Anatomy Interactive Visual Assets as Companion Pages

* **Status:** Proposed (Experimental on `feature/anatomy-visuals`, pending evaluation before merging to `main`)
* **Date:** 2026-10-20

## Context and Problem Statement

Substack posts explaining technical architectures, concurrency patterns, or system primitives often benefit from visual representations. However:
1. Traditional flowchart diagrams (boxes, arrows, abstract schemas) are sterile and often fail to convey the dynamic behavior of systems.
2. Substack strictly sanitizes post bodies for security reasons, stripping all inline `<script>` tags, WebGL canvases, and custom interactive JavaScript.

We explored integrating the philosophy and technique of [Anatomy](https://github.com/wheresryan22/anatomy) (*"The object is the explanation"*), which translates abstract concepts into tangible physical machines (e.g., fluid hoppers, pin-tumbler locks, counterweight balances) illustrated through isometric SVGs with hover inspections and interactive mechanics.

## Decision Outcome

1. **Hybrid Architecture (Substack Post + Web Companion)**:
   - Since Substack cannot render interactive scripts directly inside the newsletter body, we adopted a companion page approach:
     - The interactive machine (HTML5 + embedded SVG + CSS + JS) is generated standalone and hosted by the FastAPI server under `GET /visuals/{slug}`.
     - The Substack post receives a preformatted Markdown block containing a static preview callout and direct link:
       ```markdown
       > ⚙️ **[Título de la Máquina]** (*Metáfora: [Descripción física]*)
       > 💡 *[Explorá la máquina interactiva en vivo ↗](/visuals/{slug})*
       ```
2. **On-Demand Generation (`AnatomyGenerator`)**:
   - Visual generation is not triggered automatically to avoid unnecessary token usage and noise on simple notes.
   - It is triggered strictly on demand by the author from the Step 4 Draft panel via `POST /api/ideas/{session_id}/visuals`.
   - The prompt (`app/prompts/anatomy_prompt.md`) enforces isometric projection, four-tone technical blueprint palette (`#0f172a`, `#334155`, `#94a3b8`, `#38bdf8`), component hover tooltips, and a machine operation trigger.
3. **Storage & Observability**:
   - Visual assets are saved locally to `data/visuals/{slug}.html` (gitignored, consistent with sessions and traces).
   - All generation calls are recorded in local observability via `traced_generate(..., step="anatomy_visual")`.
4. **Current Status**:
   - Maintained on branch `feature/anatomy-visuals` pending real-world editorial evaluation and user testing before integrating into `main`.

### Positive Consequences

* Authors can complement deep technical articles with engaging, interactive visual machines without fighting Substack's HTML sanitization.
* Generates completely self-contained HTML assets without external runtime dependencies.
* Completely decoupled from core draft writing; failing or skipping visual generation does not block the editorial flow.

### Considerations & Next Steps

* Evaluate headless screenshot generation (e.g. Playwright / Chromium) to automatically attach high-resolution static PNG renders into Google Drive alongside the draft document.
* Refine machine mechanical animation richness for diverse non-concurrency topics.
