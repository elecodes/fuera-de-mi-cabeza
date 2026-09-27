# 0016. Switch Drive Export from Service Account to OAuth-as-User

* **Status:** Accepted
* **Date:** 2026-09-26

## Context and Problem Statement

ADR 0015 implemented Drive export using a Google service account: the author would share a Drive folder with the service account's email, and the backend would authenticate as that service account to create files in it. In testing, every upload failed with:
even with an empty, freshly-shared folder and plenty of free space in the author's own Drive. This is a real, well-documented Google Drive API limitation, not a misconfiguration: **service accounts have 0 GB of storage quota of their own.** Per Google's own documentation on file ownership, a file created via the Drive API is owned by whichever identity authenticated the request — a service account authenticating itself becomes the owner of any file it creates, and that file counts against the service account's own (zero) quota, regardless of how much space the folder's real owner has.

There are exactly two ways around this, and neither is available to a personal (non-Workspace) Google account:
* **Shared Drives** (formerly Team Drives) pool storage independently of any single member, so a service account added as a member can create files there. Shared Drives are a Google Workspace feature and do not exist for personal `@gmail.com` accounts.
* **Domain-wide delegation** lets a service account impersonate a real user so files are created under that user's own quota. This requires a Google Workspace domain with admin console access to grant the delegation — also unavailable on a personal account.

The author uses a personal Gmail account, so both workarounds are closed off. The only remaining option is to stop using a service account for this feature entirely.

## Decision Outcome

**Switched authentication from a service account to OAuth as the author herself**, so uploaded files are created under her own Google account and consume her own (real) storage quota — exactly as if she had created them by hand in Drive.

1. **One-time authorization script**: `scripts/authorize_google_drive.py` runs `InstalledAppFlow.from_client_secrets_file(...).run_local_server(...)` (the standard "Desktop app" OAuth flow), opening the author's browser for a one-time login and consent. The resulting credentials (including a refresh token) are saved to `GOOGLE_OAUTH_TOKEN_FILE`.
2. **`DriveUploader` now loads that token file** and, if the access token has expired, refreshes it silently using the stored refresh token (`Credentials.refresh()`), persisting the renewed token back to disk — no repeated logins needed after the initial one-time authorization.
3. **`GOOGLE_SERVICE_ACCOUNT_FILE` is replaced by `GOOGLE_OAUTH_CLIENT_SECRET_FILE` and `GOOGLE_OAUTH_TOKEN_FILE`.** The target folder no longer needs to be shared with anything — it's simply a folder in the author's own Drive, referenced by `GOOGLE_DRIVE_FOLDER_ID` as before.
4. **Same fail-loud behavior as ADR 0015**: missing client secret, missing/invalid token with no usable refresh token, or a failed Drive API call all raise a specific `RuntimeError`, never a silent no-op.
5. **New dependency**: `google-auth-oauthlib` (for `InstalledAppFlow`).
6. `google-oauth-client-secret.json` and `google-oauth-token.json` are gitignored, alongside the now-unused `google-service-account.json` pattern (kept in `.gitignore` in case anyone still has one on disk).

### Positive Consequences

* Uploads actually work on a personal Google account, which service accounts categorically cannot do here.
* No folder-sharing step needed at all — one less thing that can be misconfigured (the earlier `404 File not found` the author hit was itself a sharing/ID mismatch, now moot).

### Negative Consequences

* Requires a one-time interactive browser-based authorization step, instead of a purely headless credentials file. This is an inherent trade-off of authenticating as a real user rather than a service account, and unavoidable for a personal Google account wanting write access to its own Drive.
* If the refresh token is ever revoked (e.g., the author removes the app's access from her Google Account settings), `scripts/authorize_google_drive.py` must be run again.

## Notes from Setup

Two configuration mistakes were hit while setting this up for the first time, both worth documenting since they produce confusing, generic-looking Google error pages:

* **`Error 400: redirect_uri_mismatch`** — happens if the OAuth Client ID is created as type **"Web application"** instead of **"Desktop app"**. `InstalledAppFlow.run_local_server()` binds to a random local port each run; a "Web application" client requires a fixed, pre-registered redirect URI, which never matches. The Client ID must be type "Desktop app".
* **`Error 403: access_denied` ("has not completed the Google verification process")** — happens if the author's own Google account isn't added under **"Test users"** on the OAuth consent screen, even when she is the sole intended user of the app. The app can stay in "Testing" publishing status (avoiding Google's app verification review) as long as every account that will use it is explicitly listed as a test user.

Both are now called out explicitly in `README.md`'s setup steps.
