import io
import os

import markdown as markdown_lib
from googleapiclient.http import MediaIoBaseUpload

from app.services.google_drive_auth import build_drive_service

# NOTA HISTÓRICA (ver ADR 0016): esto usó una cuenta de servicio (ADR 0015),
# pero las cuentas de servicio tienen 0 GB de cuota propia. Para una carpeta
# en un Drive personal (no una Unidad Compartida de Workspace), cualquier
# archivo que la cuenta de servicio intente crear falla con
# `storageQuotaExceeded`, sin importar el espacio libre del dueño real de la
# carpeta. Para una cuenta de Gmail normal, sin Workspace, no hay forma de
# evitarlo con una cuenta de servicio. La alternativa es autenticar como el
# propio autor (OAuth), para que los archivos se creen bajo su propia cuenta
# y su propio espacio, tal como si los hubiera creado él mismo desde Drive.
# La carga de credenciales en sí vive en app/services/google_drive_auth.py,
# compartida con DriveReader (ver ADR 0020) para no duplicarla.

# Destinos con nombre (ver ADR 0017): cada uno es una subcarpeta de Drive
# distinta, configurada por su propia variable de entorno. "default" es la
# variable histórica GOOGLE_DRIVE_FOLDER_ID, y sirve de resguardo si alguien
# pide un destino con nombre que todavía no ha configurado.
DESTINATION_ENV_VARS = {
    "borradores": "GOOGLE_DRIVE_FOLDER_BORRADORES",
    "notes_publicados": "GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS",
    "posts_publicados": "GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS",
}
DEFAULT_DESTINATION = "borradores"


class DriveUploader:
    """
    Sube un borrador (Note o Article) a una carpeta de Google Drive como un
    Google Doc nativo, autenticando como el propio autor vía OAuth (no una
    cuenta de servicio — ver nota histórica arriba).

    Soporta varios destinos con nombre (carpeta de Borradores, Notes
    Publicados, Posts Publicados — ver DESTINATION_ENV_VARS y ADR 0017), cada
    uno configurado por su propia variable de entorno.

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
        # folder_id, si se pasa explícitamente (o vía GOOGLE_DRIVE_FOLDER_ID),
        # actúa como resguardo del destino "borradores" cuando su variable
        # con nombre específico (GOOGLE_DRIVE_FOLDER_BORRADORES) no está
        # configurada — así una configuración ya existente sigue funcionando.
        self.folder_id = folder_id or os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        self._token_file = token_file or os.getenv("GOOGLE_OAUTH_TOKEN_FILE")
        self._drive_service = drive_service  # inyectable para tests; si no, se construye bajo demanda

    def _resolve_folder_id(self, destination: str | None) -> str:
        destination = destination or DEFAULT_DESTINATION
        if destination not in DESTINATION_ENV_VARS:
            valid = ", ".join(DESTINATION_ENV_VARS.keys())
            raise RuntimeError(
                f"Destino de Drive desconocido: '{destination}'. Los válidos son: {valid}."
            )

        env_var = DESTINATION_ENV_VARS[destination]
        folder_id = os.getenv(env_var)

        # GOOGLE_DRIVE_FOLDER_ID (histórico) sirve de resguardo solo para
        # "borradores", el destino por defecto de antes de que existieran
        # varios destinos con nombre.
        if not folder_id and destination == DEFAULT_DESTINATION:
            folder_id = self.folder_id

        if not folder_id:
            raise RuntimeError(
                f"{env_var} no está configurado. "
                f"Añade el ID de la carpeta de Drive para '{destination}' en tu .env."
            )
        return folder_id

    def _get_service(self):
        if self._drive_service is not None:
            return self._drive_service
        self._drive_service = build_drive_service(self._token_file)
        return self._drive_service

    def upload_draft_as_google_doc(
        self,
        title: str | None,
        content_markdown: str,
        destination: str | None = None,
    ) -> str:
        """
        Crea un Google Doc nativo en la carpeta del destino indicado
        (ver DESTINATION_ENV_VARS; por defecto "borradores") a partir de un
        borrador en Markdown, y devuelve el enlace para abrirlo.
        """
        folder_id = self._resolve_folder_id(destination)
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
            "parents": [folder_id],
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
