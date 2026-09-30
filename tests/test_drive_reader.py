import pytest

from app.services.drive_reader import DriveReader


class _FakeFilesList:
    def __init__(self, response):
        self._response = response

    def execute(self):
        return self._response


class _FakeFilesExport:
    def __init__(self, content, error=None):
        self._content = content
        self._error = error

    def execute(self):
        if self._error:
            raise self._error
        return self._content


class _FakeFiles:
    def __init__(self, list_response=None, export_content=None, export_error=None, captured_list_calls=None):
        self._list_response = list_response or {"files": []}
        self._export_content = export_content
        self._export_error = export_error
        self._captured_list_calls = captured_list_calls

    def list(self, q, fields, supportsAllDrives=None, includeItemsFromAllDrives=None):
        if self._captured_list_calls is not None:
            self._captured_list_calls.append({"q": q})
        return _FakeFilesList(self._list_response)

    def export(self, fileId, mimeType):
        return _FakeFilesExport(self._export_content, error=self._export_error)


class _FakeDriveService:
    def __init__(self, list_response=None, export_content=None, export_error=None, captured_list_calls=None):
        self._files = _FakeFiles(
            list_response=list_response,
            export_content=export_content,
            export_error=export_error,
            captured_list_calls=captured_list_calls,
        )

    def files(self):
        return self._files


def test_list_documents_returns_files_and_filters_by_folder():
    calls = []
    fake_response = {"files": [{"id": "abc", "name": "Mi post", "modifiedTime": "2026-09-01T00:00:00Z"}]}
    service = _FakeDriveService(list_response=fake_response, captured_list_calls=calls)
    reader = DriveReader(drive_service=service)

    docs = reader.list_documents("folder-xyz")

    assert docs == fake_response["files"]
    assert "folder-xyz" in calls[0]["q"]


def test_list_documents_raises_on_api_error():
    class _FailingFiles:
        def list(self, **kwargs):
            raise Exception("403 Forbidden")

    class _FailingService:
        def files(self):
            return _FailingFiles()

    reader = DriveReader(drive_service=_FailingService())
    with pytest.raises(RuntimeError, match="403 Forbidden"):
        reader.list_documents("folder-xyz")


def test_export_document_text_decodes_bytes():
    service = _FakeDriveService(export_content=b"Hola, este es el texto exportado.")
    reader = DriveReader(drive_service=service)

    text = reader.export_document_text("file-id")

    assert text == "Hola, este es el texto exportado."


def test_export_document_text_raises_on_api_error():
    service = _FakeDriveService(export_error=Exception("404 Not Found"))
    reader = DriveReader(drive_service=service)

    with pytest.raises(RuntimeError, match="404 Not Found"):
        reader.export_document_text("file-id")
