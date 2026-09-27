# 0017. Named Destinations for Drive Export (Borradores / Notes Publicados / Posts Publicados)

* **Status:** Accepted
* **Date:** 2026-09-27

## Context and Problem Statement

ADR 0015/0016 added a single Drive export destination, configured by one `GOOGLE_DRIVE_FOLDER_ID`. The author organizes her Drive with separate subfolders for different stages of a piece — drafts, published Notes, and published Posts — and wants to choose which one a given export goes to, rather than always landing in the same folder.

## Decision Outcome

1. **Three named destinations**, each its own environment variable:
   - `borradores` → `GOOGLE_DRIVE_FOLDER_BORRADORES`
   - `notes_publicados` → `GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS`
   - `posts_publicados` → `GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS`

   `DriveUploader.DESTINATION_ENV_VARS` holds this mapping; `upload_draft_as_google_doc(title, content_markdown, destination=None)` resolves the right folder ID at call time. `destination=None` defaults to `"borradores"`.
2. **Backward compatibility**: the historical `GOOGLE_DRIVE_FOLDER_ID` still works as a fallback specifically for the `"borradores"` destination, so an existing `.env` from before this change keeps working without edits.
3. **Fail loud per destination**: an unknown destination name, or a valid destination whose specific environment variable isn't set (and, for `"borradores"`, no legacy fallback either), raises a `RuntimeError` naming exactly which environment variable is missing — never a silent fallback to the wrong folder.
4. **UI**: a `<select>` next to the "📤 Guardar en Google Drive" button lets the author choose the destination before exporting; the choice is sent as `{"destination": "..."}` in the `POST /api/ideas/{session_id}/export-to-drive` request body (optional — omitting it defaults to `"borradores"`, preserving the old one-argument behavior for any other caller).
5. Folders can be Drive subfolders at any depth — nothing here is folder-hierarchy-aware, since Drive's own "parent" model already handles nesting. The author only needs each destination's own folder ID, found in that folder's URL, regardless of how deep it's nested.

### Positive Consequences

* The author can route a given export to the right stage of her workflow without touching `.env` or restarting the backend each time.
* Nothing breaks for a `.env` that only has the legacy `GOOGLE_DRIVE_FOLDER_ID` set.

### Considered but Not Done

* A fully dynamic/arbitrary folder picker (e.g., browsing the author's Drive tree from the UI) was not built — three fixed, named destinations match her actual workflow (draft, published note, published post) and are far simpler to configure and reason about than a general-purpose folder browser.
