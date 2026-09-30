from app.services.google_drive_auth import build_drive_service


class DriveReader:
    """
    Lee documentos de una carpeta de Drive: los lista y exporta su texto.

    Usa las mismas credenciales OAuth que `DriveUploader` (ver
    `app/services/google_drive_auth.py`) — no hace falta una autorización
    aparte para leer, ya que el alcance ya cubre lectura y escritura.
    """

    def __init__(self, drive_service=None, token_file: str | None = None):
        self._token_file = token_file
        self._drive_service = drive_service  # inyectable para tests

    def _get_service(self):
        if self._drive_service is not None:
            return self._drive_service
        self._drive_service = build_drive_service(self._token_file)
        return self._drive_service

    def list_documents(self, folder_id: str) -> list[dict]:
        """Devuelve [{id, name, modifiedTime, webViewLink}] de los Google Docs en la carpeta."""
        service = self._get_service()
        try:
            response = (
                service.files()
                .list(
                    q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false",
                    fields="files(id, name, modifiedTime, webViewLink)",
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Error al listar documentos de la carpeta '{folder_id}': {e}") from e
        return response.get("files", [])

    def export_document_text(self, file_id: str) -> str:
        """Exporta el contenido de un Google Doc como texto plano."""
        service = self._get_service()
        try:
            content = service.files().export(fileId=file_id, mimeType="text/plain").execute()
        except Exception as e:
            raise RuntimeError(f"Error al exportar el documento '{file_id}': {e}") from e
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="replace")
        return str(content)
