# 0015. Export Drafts to Google Drive as Native Google Docs

* **Status:** Accepted
* **Date:** 2026-09-26

## Context and Problem Statement

The author asked for a way to save generated Notes/Articles into a Google Drive folder, as native, editable Google Docs, triggered by a button (not automatically on every generation).

## Decision Drivers

* **No user-facing OAuth flow**: this is a personal, single-user backend. A consent-screen OAuth flow (with refresh token storage and expiry handling) is the right design for a multi-user app, but is unnecessary complexity here.
* **Native Google Doc, not a `.md`/`.txt` file**: the author wants to open and keep editing the piece directly in Drive/Docs.
* **Consistency**: any failure (missing credentials, unshared folder, API error) must surface as a real, visible error — never a silent no-op or a fake success, per the pattern established in ADR 0009, 0012, and 0013.

## Decision Outcome

1. **Authentication via a Google service account**, not user OAuth. The author creates a service account in Google Cloud, downloads its JSON key, and shares the target Drive folder with the service account's email (as an Editor) — the same mental model as sharing a folder with a collaborator. This needs no interactive login and no token refresh logic. Full setup steps are documented in `README.md` under "Exportar a Google Drive".
2. **Scope: `https://www.googleapis.com/auth/drive`** (not the narrower `drive.file`). `drive.file` only grants access to files the app itself created or that a user explicitly opened through a file picker; it does not reliably grant access to a folder shared with the service account by ID, which is exactly this feature's access pattern.
3. **Markdown → HTML → native Google Doc.** The Drive API can import a file and convert it directly into a native Google Doc (`mimeType: application/vnd.google-apps.document`) at upload time. `text/html` has long been a broadly and reliably supported import source, so the draft's Markdown is first converted to HTML (via the `markdown` package) and uploaded with `mimeType="text/html"` as the upload media type, letting Drive's import step produce the native Doc with headings, bold, and lists already applied.
4. **New service `app/services/drive_uploader.py` (`DriveUploader`)**, following the same dependency-injection pattern as `LLMClient`: it accepts an optional `drive_service` for tests, and only builds a real `googleapiclient` service lazily, on first real use. It raises `RuntimeError` with a specific, actionable message for every failure mode (missing `GOOGLE_SERVICE_ACCOUNT_FILE`, missing credentials file on disk, missing `GOOGLE_DRIVE_FOLDER_ID`, empty draft content, the Drive API call itself failing, or Drive returning no `webViewLink`) — never a silent failure.
5. **New endpoint `POST /api/ideas/{session_id}/export-to-drive`**, following the same pattern as every other session endpoint (`session_manager.get_session`, 400 if the precondition isn't met, `try/except` wrapping the real work into a 500 with the underlying error). It reads the draft's current `title`/`content` from the session (already includes any unsaved textarea edits, since the frontend calls `saveDraftChanges()` immediately before exporting), so there is nothing new to keep in sync.
6. **Manual trigger only**: a "📤 Guardar en Google Drive" button next to the existing "📋 Copiar borrador" button. No automatic upload on generation or revision — the author explicitly asked for a button, not an automatic save.
7. **New dependencies**: `google-api-python-client`, `google-auth`, `markdown`.
8. **`google-service-account.json` is gitignored** (`*service-account*.json` pattern added to `.gitignore`), so the credentials file can never be committed by accident.

### Positive Consequences

* The author can go from generated draft to an editable, shareable Google Doc in one click, with no separate login step.
* Every failure mode has a specific, human-readable message, consistent with the rest of the project's "fail loud" philosophy.

### Considered but Not Done

* **User OAuth flow**: not needed for a single-user tool; would add token storage/refresh complexity with no real benefit here.
* **Automatic export on generation/revision**: explicitly declined by the author in favor of a manual button, to keep control over what actually lands in Drive.
* **Uploading as `.md`/`.txt` instead of a native Doc**: the author specifically wants something editable directly in Drive, not a plain file.
