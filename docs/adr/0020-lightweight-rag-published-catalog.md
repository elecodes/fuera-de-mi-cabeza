# 0020. Lightweight RAG Over the Author's Own Published Catalog

* **Status:** Accepted
* **Date:** 2026-09-28

## Context and Problem Statement

The author asked whether a RAG (retrieval-augmented generation) system would be useful for the app, and separately confirmed she wants one. The genuine value identified for this project isn't generic knowledge retrieval — it's narrower and more useful: letting the author know, while exploring a new idea, whether she has already written something similar, so she can avoid unknowingly repeating herself or deliberately build on an earlier piece.

Two design questions had to be resolved before building anything:
1. **Where does the published catalog live?** The author already keeps her published Notes and Posts in the same two Drive folders the export feature (ADR 0017) already writes to — `GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS` and `GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS`. No new storage or manual copying is needed; the ingestion step reads from folders that already exist and are already populated by the app's own export flow.
2. **Which embeddings provider?** The author chose Gemini's `gemini-embedding-001`, which has a free tier and is more than sufficient at this usage rate (embedding happens only when ingesting a changed document, and once per idea exploration — nowhere near free-tier limits for personal use).

## Decision Drivers

* **No inventing on the model's behalf**: the retrieved matches are shown to the author as direct links to her own real documents, not summarized or paraphrased by the LLM and not injected into the generation prompt. This avoids the retrieval step becoming a second, less-controlled path for the model to reference (and possibly misrepresent) her past work.
* **No new infrastructure**: at a personal catalog's scale (tens to a few hundred pieces), a vector database is unnecessary. A JSON file plus a cosine-similarity comparison in plain Python is simpler to run, inspect, and back up.
* **Reuse what already exists**: the OAuth credentials and folder configuration from ADR 0016/0017 are reused as-is, so there is no separate "connect this to Drive" step for this feature — indexing is one script, `scripts/ingest_published_drive_docs.py`, run manually whenever the author wants to refresh the catalog (e.g., after publishing something new).

## Decision Outcome

1. **`app/services/embeddings_client.py` (`GeminiEmbeddingsClient`)**: a small httpx-based client for Gemini's `embedContent` endpoint, matching the project's existing preference for lightweight custom HTTP clients over SDKs (see `openai_client.py`). Distinguishes `task_type="RETRIEVAL_DOCUMENT"` (when indexing) from `"RETRIEVAL_QUERY"` (when searching) — Gemini optimizes the embedding space differently for each side of an asymmetric search, and using the matching type materially improves retrieval quality.
2. **`app/services/knowledge_base.py` (`KnowledgeBase`)**: stores `{doc_id: {title, text, embedding, source_link, modified_time}}` in `data/knowledge_base.json` (gitignored — personal content, same treatment as `voice_samples.md` and `data/sessions/`). `search(query_embedding, top_k)` ranks by cosine similarity, computed in plain Python (no numpy dependency added).
3. **`app/services/google_drive_auth.py`**: the OAuth credential-loading logic was extracted out of `DriveUploader` into this shared module, so the new `DriveReader` (read-only: list + export Google Docs from a folder) can reuse the exact same authenticated client instead of duplicating the loading/refresh logic. `DriveUploader` was refactored to use it too; its existing test suite was re-run in full to confirm no behavior change.
4. **`scripts/ingest_published_drive_docs.py`**: reads both published-content folders, skips any document whose Drive `modifiedTime` hasn't changed since the last run (avoiding redundant embedding calls), and stores the rest in the knowledge base. Run manually, not on a schedule.
5. **`POST /api/knowledge/search`**: embeds the given query text and returns the top-k most similar stored pieces (title, link, score). Follows the same fail-loud pattern as every other endpoint in this project — a missing `GEMINI_API_KEY` or an API failure surfaces as a real error, not a silent empty result.
6. **Frontend**: after exploring a new idea, the UI calls this endpoint with the idea's own text and shows a **"📚 Ya escribiste algo parecido"** panel with links, only for matches scoring ≥ 0.75 cosine similarity. This call is wrapped to fail silently (not an `alert()`) if the knowledge base isn't configured yet or the search fails — it's an auxiliary, informational feature, not part of the core idea-exploration path, and its absence must never block or interrupt the main flow.
7. **Explicitly not done in this version**: retrieved content is not injected into any generation prompt. The author sees links to her own real pieces; the LLM never receives or paraphrases their content. This is a deliberate scope boundary for v1, not an oversight — folding retrieved excerpts into `draft_generator`/`content_planner` prompts is a reasonable v2 step once the retrieval quality itself has been used and judged for a while.

### Positive Consequences

* Reuses existing Drive folders and OAuth setup entirely — no new connection step for the author.
* Very low cost and complexity: no vector database, one small HTTP client, one JSON file.
* Never puts the author's past writing through the LLM without her explicit say-so.

### Considered but Not Done

* Injecting retrieved excerpts into generation prompts (deferred to a possible v2, see point 7 above).
* A scheduled/automatic re-indexing trigger — indexing stays a manual, author-run step for now, consistent with the Drive export button also being manual (ADR 0017 rejected automatic export for the same reason: keeping control over what enters the pipeline).
