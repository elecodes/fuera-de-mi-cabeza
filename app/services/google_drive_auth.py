from pathlib import Path

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Mismo alcance que DriveUploader (ver ADR 0016): acceso completo a Drive,
# necesario para leer y escribir en carpetas que no fueron creadas por esta
# app. `drive.readonly` bastaría para solo lectura, pero usar un único
# alcance para todo evita pedir una segunda autorización si más adelante
# hiciera falta también escribir desde el mismo cliente.
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive"]


def build_drive_service(token_file: str | None):
    """
    Carga el token de OAuth generado por `scripts/authorize_google_drive.py`,
    lo renueva si ha caducado (guardando el token renovado de vuelta en
    disco), y devuelve un cliente de la API de Drive ya autenticado.

    Falla de forma visible (RuntimeError) si falta el archivo de token o no
    se puede renovar — nunca en silencio (ver ADR 0009, 0012, 0013).
    """
    if not token_file:
        raise RuntimeError(
            "GOOGLE_OAUTH_TOKEN_FILE no está configurado. "
            "Ejecuta 'python3 scripts/authorize_google_drive.py' para autorizar el acceso a Drive."
        )
    if not Path(token_file).exists():
        raise RuntimeError(
            f"No se encontró el archivo de autorización en '{token_file}'. "
            "Ejecuta 'python3 scripts/authorize_google_drive.py' primero (una sola vez)."
        )

    credentials = Credentials.from_authorized_user_file(token_file, DRIVE_SCOPES)

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
            Path(token_file).write_text(credentials.to_json(), encoding="utf-8")
        else:
            raise RuntimeError(
                "El token de Google Drive no es válido y no tiene refresh token. "
                "Vuelve a ejecutar 'python3 scripts/authorize_google_drive.py'."
            )

    return build("drive", "v3", credentials=credentials)
