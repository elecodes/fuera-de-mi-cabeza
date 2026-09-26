import io
import os
from pathlib import Path

import markdown as markdown_lib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Alcance completo de Drive: una cuenta de servicio solo puede escribir en una
# carpeta que el autor ha compartido con ella explícitamente (como si fuera un
# colaborador más). El alcance restringido `drive.file` no basta aquí, porque
# solo cubre archivos que la propia app crea o que el usuario abre a través de
# un selector de archivos — no una carpeta ajena compartida por ID.
_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


class DriveUploader:
    """
    Sube un borrador (Note o Article) a una carpeta de Google Drive como un
    Google Doc nativo, usando una cuenta de servicio.

    Falla de forma visible (RuntimeError con un mensaje claro) si faltan
    credenciales, falta el ID de la carpeta, o la llamada a la API de Drive
    falla — nunca en silencio, siguiendo el mismo principio que el resto del
    proyecto (ver ADR 0009, 0012, 0013).
    """

    def __init__(
        self,
        drive_service=None,
        folder_id: str | None = None,
        service_account_file: str | None = None,
    ):
        self.folder_id = folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self._service_account_file = service_account_file or os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        self._drive_service = drive_service  # inyectable para tests; si no, se construye bajo demanda

    def _get_service(self):
        if self._drive_service is not None:
            return self._drive_service

        if not self._service_account_file:
            raise RuntimeError(
                "GOOGLE_SERVICE_ACCOUNT_FILE no está configurado. "
                "Añade la ruta al JSON de la cuenta de servicio en tu .env."
            )
        if not Path(self._service_account_file).exists():
            raise RuntimeError(
                f"No se encontró el archivo de credenciales en '{self._service_account_file}'. "
                "Revisa la ruta en GOOGLE_SERVICE_ACCOUNT_FILE."
            )

        credentials = service_account.Credentials.from_service_account_file(
            self._service_account_file, scopes=_DRIVE_SCOPES
        )
        self._drive_service = build("drive", "v3", credentials=credentials)
        return self._drive_service

    def upload_draft_as_google_doc(self, title: str | None, content_markdown: str) -> str:
        """
        Crea un Google Doc nativo en la carpeta configurada a partir de un
        borrador en Markdown, y devuelve el enlace para abrirlo.
        """
        if not self.folder_id:
            raise RuntimeError(
                "GOOGLE_DRIVE_FOLDER_ID no está configurado. "
                "Añade el ID de la carpeta de Drive (compartida con la cuenta de servicio) en tu .env."
            )
        if not content_markdown or not content_markdown.strip():
            raise RuntimeError("El borrador está vacío: no hay nada que subir a Drive.")

        service = self._get_service()

        # Google Docs no entiende Markdown directamente, pero sí sabe importar
        # HTML y convertirlo a un documento nativo con el formato (negritas,
        # títulos, listas) ya aplicado. Por eso se convierte a HTML primero.
        html_content = markdown_lib.markdown(content_markdown)
        media = MediaIoBaseUpload(
            io.BytesIO(html_content.encode("utf-8")),
            mimetype="text/html",
            resumable=False,
        )
        file_metadata = {
            "name": (title or "Borrador sin título").strip(),
            "mimeType": "application/vnd.google-apps.document",
            "parents": [self.folder_id],
        }

        try:
            created_file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id, webViewLink")
                .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Error al subir el borrador a Google Drive: {e}") from e

        link = created_file.get("webViewLink")
        if not link:
            raise RuntimeError(
                "Google Drive creó el documento pero no devolvió un enlace (webViewLink)."
            )
        return link
