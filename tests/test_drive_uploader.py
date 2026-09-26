import pytest
from app.services.drive_uploader import DriveUploader


class _FakeFilesCreate:
    def __init__(self, response=None, error=None):
        self._response = response
        self._error = error

    def execute(self):
        if self._error:
            raise self._error
        return self._response


class _FakeFiles:
    def __init__(self, response=None, error=None, captured_calls=None):
        self._response = response
        self._error = error
        self._captured_calls = captured_calls

    def create(self, body, media_body, fields):
        if self._captured_calls is not None:
            self._captured_calls.append({"body": body, "fields": fields})
        return _FakeFilesCreate(response=self._response, error=self._error)


class _FakeDriveService:
    def __init__(self, response=None, error=None, captured_calls=None):
        self._files = _FakeFiles(response=response, error=error, captured_calls=captured_calls)

    def files(self):
        return self._files


def test_upload_draft_creates_native_google_doc_in_configured_folder():
    calls = []
    fake_service = _FakeDriveService(
        response={"id": "abc123", "webViewLink": "https://docs.google.com/document/d/abc123/edit"},
        captured_calls=calls,
    )
    uploader = DriveUploader(drive_service=fake_service, folder_id="folder-xyz")

    link = uploader.upload_draft_as_google_doc(
        title="Mi borrador",
        content_markdown="# Título\n\nUn párrafo con **negrita**.",
    )

    assert link == "https://docs.google.com/document/d/abc123/edit"
    assert len(calls) == 1
    body = calls[0]["body"]
    assert body["name"] == "Mi borrador"
    assert body["mimeType"] == "application/vnd.google-apps.document"
    assert body["parents"] == ["folder-xyz"]


def test_upload_draft_defaults_title_when_none():
    fake_service = _FakeDriveService(
        response={"id": "abc123", "webViewLink": "https://docs.google.com/document/d/abc123/edit"}
    )
    uploader = DriveUploader(drive_service=fake_service, folder_id="folder-xyz")

    link = uploader.upload_draft_as_google_doc(title=None, content_markdown="Contenido de una nota.")

    assert link.startswith("https://docs.google.com")


def test_upload_draft_raises_without_folder_id():
    uploader = DriveUploader(drive_service=_FakeDriveService(), folder_id=None)

    with pytest.raises(RuntimeError, match="GOOGLE_DRIVE_FOLDER_ID"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_upload_draft_raises_on_empty_content():
    uploader = DriveUploader(drive_service=_FakeDriveService(), folder_id="folder-xyz")

    with pytest.raises(RuntimeError, match="vacío"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="   ")


def test_upload_draft_raises_when_drive_api_call_fails():
    fake_service = _FakeDriveService(error=Exception("403 Forbidden"))
    uploader = DriveUploader(drive_service=fake_service, folder_id="folder-xyz")

    with pytest.raises(RuntimeError, match="403 Forbidden"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_upload_draft_raises_when_drive_returns_no_link():
    fake_service = _FakeDriveService(response={"id": "abc123"})  # sin webViewLink
    uploader = DriveUploader(drive_service=fake_service, folder_id="folder-xyz")

    with pytest.raises(RuntimeError, match="webViewLink"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_get_service_raises_without_credentials_file_configured():
    uploader = DriveUploader(drive_service=None, folder_id="folder-xyz", service_account_file=None)

    with pytest.raises(RuntimeError, match="GOOGLE_SERVICE_ACCOUNT_FILE"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_get_service_raises_when_credentials_file_missing(tmp_path):
    missing_path = tmp_path / "no-existe.json"
    uploader = DriveUploader(
        drive_service=None,
        folder_id="folder-xyz",
        service_account_file=str(missing_path),
    )

    with pytest.raises(RuntimeError, match="No se encontró el archivo de credenciales"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")
