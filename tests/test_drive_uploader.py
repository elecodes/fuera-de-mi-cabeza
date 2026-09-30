from unittest.mock import MagicMock, patch

import pytest
from app.services.drive_uploader import DriveUploader


@pytest.fixture(autouse=True)
def _clear_real_drive_env(monkeypatch):
    # Aísla TODOS los tests de este archivo de las variables de Drive reales
    # que pueda tener configuradas la máquina en su .env (se cargan al
    # importar app.main durante la recolección de tests). Sin esto, un test
    # que espera un folder_id concreto puede fallar en silencio si la máquina
    # ya tiene una carpeta real configurada para ese mismo destino.
    for var in [
        "GOOGLE_DRIVE_FOLDER_ID",
        "GOOGLE_DRIVE_FOLDER_BORRADORES",
        "GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS",
        "GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS",
        "GOOGLE_OAUTH_TOKEN_FILE",
    ]:
        monkeypatch.delenv(var, raising=False)


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

    def create(self, body, media_body, fields, supportsAllDrives=None):
        if self._captured_calls is not None:
            self._captured_calls.append({"body": body, "fields": fields, "supportsAllDrives": supportsAllDrives})
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
    assert calls[0]["supportsAllDrives"] is True


def test_upload_draft_defaults_title_when_none():
    fake_service = _FakeDriveService(
        response={"id": "abc123", "webViewLink": "https://docs.google.com/document/d/abc123/edit"}
    )
    uploader = DriveUploader(drive_service=fake_service, folder_id="folder-xyz")

    link = uploader.upload_draft_as_google_doc(title=None, content_markdown="Contenido de una nota.")

    assert link.startswith("https://docs.google.com")


def test_upload_draft_raises_without_folder_id(monkeypatch):
    # Aísla el test del .env real: si las variables de carpeta están
    # configuradas en la máquina (como debería ser en uso normal), este test
    # necesita comprobar el caso en que NO lo están, sin que el .env real se cuele.
    monkeypatch.delenv("GOOGLE_DRIVE_FOLDER_ID", raising=False)
    monkeypatch.delenv("GOOGLE_DRIVE_FOLDER_BORRADORES", raising=False)
    uploader = DriveUploader(drive_service=_FakeDriveService(), folder_id=None)

    with pytest.raises(RuntimeError, match="GOOGLE_DRIVE_FOLDER_BORRADORES"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_upload_draft_destination_borradores_falls_back_to_legacy_folder_id(monkeypatch):
    # GOOGLE_DRIVE_FOLDER_ID (histórico, de antes de que existieran varios
    # destinos con nombre) sigue sirviendo como resguardo, pero solo para
    # el destino "borradores".
    monkeypatch.delenv("GOOGLE_DRIVE_FOLDER_BORRADORES", raising=False)
    calls = []
    fake_service = _FakeDriveService(
        response={"id": "abc123", "webViewLink": "https://docs.google.com/document/d/abc123/edit"},
        captured_calls=calls,
    )
    uploader = DriveUploader(drive_service=fake_service, folder_id="legacy-folder-id")

    uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido", destination="borradores")

    assert calls[0]["body"]["parents"] == ["legacy-folder-id"]


def test_upload_draft_routes_to_the_right_named_destination(monkeypatch):
    monkeypatch.setenv("GOOGLE_DRIVE_FOLDER_BORRADORES", "id-borradores")
    monkeypatch.setenv("GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS", "id-notes")
    monkeypatch.setenv("GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS", "id-posts")

    for destination, expected_folder in [
        ("borradores", "id-borradores"),
        ("notes_publicados", "id-notes"),
        ("posts_publicados", "id-posts"),
        (None, "id-borradores"),  # sin destino explícito, usa "borradores" por defecto
    ]:
        calls = []
        fake_service = _FakeDriveService(
            response={"id": "x", "webViewLink": "https://docs.google.com/document/d/x/edit"},
            captured_calls=calls,
        )
        uploader = DriveUploader(drive_service=fake_service)
        uploader.upload_draft_as_google_doc(title="T", content_markdown="C", destination=destination)
        assert calls[0]["body"]["parents"] == [expected_folder]


def test_upload_draft_raises_for_unknown_destination():
    uploader = DriveUploader(drive_service=_FakeDriveService(), folder_id="folder-xyz")

    with pytest.raises(RuntimeError, match="Destino de Drive desconocido"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido", destination="carpeta_inventada")


def test_upload_draft_raises_when_named_destination_not_configured(monkeypatch):
    monkeypatch.delenv("GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS", raising=False)
    uploader = DriveUploader(drive_service=_FakeDriveService(), folder_id="folder-xyz")

    with pytest.raises(RuntimeError, match="GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido", destination="notes_publicados")


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


def test_get_service_raises_without_token_file_configured(monkeypatch):
    # Mismo motivo que arriba: aísla del GOOGLE_OAUTH_TOKEN_FILE real del .env.
    monkeypatch.delenv("GOOGLE_OAUTH_TOKEN_FILE", raising=False)
    uploader = DriveUploader(drive_service=None, folder_id="folder-xyz", token_file=None)

    with pytest.raises(RuntimeError, match="GOOGLE_OAUTH_TOKEN_FILE"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_get_service_raises_when_token_file_missing(tmp_path):
    missing_path = tmp_path / "no-existe.json"
    uploader = DriveUploader(
        drive_service=None,
        folder_id="folder-xyz",
        token_file=str(missing_path),
    )

    with pytest.raises(RuntimeError, match="No se encontró el archivo de autorización"):
        uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")


def test_get_service_refreshes_expired_token_and_persists_it(tmp_path, monkeypatch):
    token_file = tmp_path / "token.json"
    token_file.write_text("{}", encoding="utf-8")

    fake_creds = MagicMock()
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refresh_token = "a-refresh-token"
    fake_creds.to_json.return_value = '{"renewed": true}'

    def fake_refresh(request):
        fake_creds.valid = True  # simula que tras refrescar, ya es válido

    fake_creds.refresh.side_effect = fake_refresh

    fake_built_service = _FakeDriveService(
        response={"id": "x", "webViewLink": "https://docs.google.com/document/d/x/edit"}
    )

    with patch("app.services.google_drive_auth.Credentials.from_authorized_user_file", return_value=fake_creds), \
         patch("app.services.google_drive_auth.build", return_value=fake_built_service) as mock_build:
        uploader = DriveUploader(drive_service=None, folder_id="folder-xyz", token_file=str(token_file))
        link = uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")

    assert link == "https://docs.google.com/document/d/x/edit"
    fake_creds.refresh.assert_called_once()
    mock_build.assert_called_once()
    # El token renovado se guarda de vuelta en disco.
    assert token_file.read_text(encoding="utf-8") == '{"renewed": true}'


def test_get_service_raises_when_token_expired_without_refresh_token(tmp_path):
    token_file = tmp_path / "token.json"
    token_file.write_text("{}", encoding="utf-8")

    fake_creds = MagicMock()
    fake_creds.valid = False
    fake_creds.expired = True
    fake_creds.refresh_token = None

    with patch("app.services.google_drive_auth.Credentials.from_authorized_user_file", return_value=fake_creds):
        uploader = DriveUploader(drive_service=None, folder_id="folder-xyz", token_file=str(token_file))
        with pytest.raises(RuntimeError, match="no tiene refresh token"):
            uploader.upload_draft_as_google_doc(title="T", content_markdown="Contenido")
