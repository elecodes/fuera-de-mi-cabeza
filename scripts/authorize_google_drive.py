"""
Autoriza 'Fuera de mi cabeza' para crear Google Docs en tu propio Drive.

Se ejecuta UNA SOLA VEZ (o cada vez que borres/pierdas el archivo de token).
Abre tu navegador, inicias sesión con tu cuenta de Google, aceptas el acceso
a Drive, y el script guarda un archivo de token que el backend usa a partir
de ahí para renovarse solo, sin volver a pedirte nada.

Uso:
    python3 scripts/authorize_google_drive.py

Requiere en tu .env (o pasados por variable de entorno):
    GOOGLE_OAUTH_CLIENT_SECRET_FILE  (por defecto: google-oauth-client-secret.json)
    GOOGLE_OAUTH_TOKEN_FILE          (por defecto: google-oauth-token.json)

Ver README.md, sección "Exportar a Google Drive", para los pasos completos
de creación del Client ID de OAuth en Google Cloud Console.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]


def main() -> None:
    load_dotenv()

    client_secret_file = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET_FILE", "google-oauth-client-secret.json")
    token_file = os.getenv("GOOGLE_OAUTH_TOKEN_FILE", "google-oauth-token.json")

    if not Path(client_secret_file).exists():
        print(f"❌ No se encontró '{client_secret_file}'.")
        print(
            "   Descárgalo desde Google Cloud Console → APIs y servicios → Credenciales → "
            "tu Client ID de OAuth (tipo 'App de escritorio') → botón de descarga."
        )
        print("   Ver README.md, sección 'Exportar a Google Drive', para los pasos completos.")
        sys.exit(1)

    print("🔐 Abriendo el navegador para autorizar el acceso a Google Drive...")
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
    credentials = flow.run_local_server(port=0)

    Path(token_file).write_text(credentials.to_json(), encoding="utf-8")
    print(f"✅ Autorización guardada en '{token_file}'.")
    print("   Ya puedes usar el botón 'Guardar en Google Drive' en la app.")


if __name__ == "__main__":
    main()
