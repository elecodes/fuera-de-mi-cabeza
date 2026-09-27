import io
import os
from pathlib import Path

import markdown as markdown_lib
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# NOTA HISTÓRICA (ver ADR 0016): esto usó una cuenta de servicio (ADR 0015),
# pero las cuentas de servicio tienen 0 GB de cuota propia. Para una carpeta
# en un Drive personal (no una Unidad Compartida de Workspace), cualquier
# archivo que la cuenta de servicio intente crear falla con
# `storageQuotaExceeded`, sin importar el espacio libre del dueño real de la
# carpeta. Para una cuenta de Gmail normal, sin Workspace, no hay forma de
# evitarlo con una cuenta de servicio. La alternativa es autenticar como el
# propio autor (OAuth), para que los archivos se creen bajo su propia cuenta
# y su propio espacio, tal como si los hubiera creado él mismo desde Drive.
_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


class DriveUploader:
    """
    Sube un borrador (Note o Article) a una carpeta de Google Drive como un
    Google Doc nativo, autenticando como el propio autor vía OAuth (no una
    cuenta de servicio — ver nota histórica arriba).

    Requiere que `scripts/authorize_google_drive.py` se haya ejecutado una
    vez para generar el archivo de token (GOOGLE_OAUTH_TOKEN_FILE). A partir
    de ahí, el token se renueva solo (usando el refresh token) sin volver a
    pedir autorización.

    Falla de forma visible (RuntimeError con un mensaje claro) si faltan
    credenciales, falta el ID de la carpeta, o la llamada a la API de Drive
    falla — nunca en silencio, siguiendo el mismo principio que el resto del
    proyecto (ver ADR 0009, 0012, 0013).
    """

    def __init__(
        self,
        drive_service=None,
        folder_id: str | None = None,
        token_file: str | None = None,
    ):
        self.folder_id = folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self._token_file = token_file or os.getenv("GOOGLE_OAUTH_TOKEN_FILE")
        self._drive_service = drive_service  # inyectable para tests; si no, se construye bajo demanda

    def _get_service(self):
        if self._drive_service is not None:
            return self._drive_service

        if not self._token_file:
            raise RuntimeError(
                "GOOGLE_OAUTH_TOKEN_FILE no está configurado. "
                "Ejecuta 'python3 scripts/authorize_google_drive.py' para autorizar el acceso a Drive."
            )
        if not Path(self._token_file).exists():
            raise RuntimeError(
                f"No se encontró el archivo de autorización en '{self._token_file}'. "
                "Ejecuta 'python3 scripts/authorize_google_drive.py' primero (una sola vez)."
            )

        credentials = Credentials.from_authorized_user_file(self._token_file, _DRIVE_SCOPES)

        if not credentials.valid:
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(GoogleAuthRequest())
                except Exception as e:
                    raise RuntimeError(
                        "El token de Google Drive caducó y no se pudo renovar automáticamente. "
                        "Vuelve a ejecutar 'python3 scripts/authorize_google_drive.py'."
                    ) from e
                # El access token cambia al renovarse; se guarda de vuelta para no
                # tener que renovarlo otra vez en la próxima llamada.
                Path(self._token_file).write_text(credentials.to_json(), encoding="utf-8")
            else:
                raise RuntimeError(
                    "El token de Google Drive no es válido y no tiene refresh token. "
                    "Vuelve a ejecutar 'python3 scripts/authorize_google_drive.py'."
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
                "Añade el ID de una carpeta de tu propio Drive en tu .env."
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
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id, webViewLink",
                    supportsAllDrives=True,
                )
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
