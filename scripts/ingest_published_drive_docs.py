"""
Indexa los Notes y Posts ya publicados (en las carpetas de Drive configuradas
en GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS y GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS)
en el almacén local de conocimiento, para poder buscarlos por significado al
explorar una idea nueva.

No es automático: se ejecuta a mano cuando quieras refrescar el índice
(por ejemplo, después de publicar algo nuevo). Solo reindexa lo que haya
cambiado desde la última vez (compara por la fecha de modificación de Drive).

Uso:
    python3 scripts/ingest_published_drive_docs.py

Requiere en tu .env:
    GOOGLE_OAUTH_TOKEN_FILE                 (ya usado por el botón de Drive)
    GEMINI_API_KEY
    GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS    (opcional si no usas ese destino)
    GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS    (opcional si no usas ese destino)
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

from app.services.drive_reader import DriveReader
from app.services.embeddings_client import GeminiEmbeddingsClient
from app.services.knowledge_base import KnowledgeBase

FOLDERS_TO_INDEX = {
    "notes_publicados": "GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS",
    "posts_publicados": "GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS",
}

# Los embeddings de Gemini tienen un límite de tokens de entrada; para un
# post largo, cortar a los primeros ~6000 caracteres es de sobra para
# capturar el tema y el enfoque sin acercarse al límite.
MAX_CHARS_PER_DOC = 6000


async def main() -> None:
    load_dotenv()

    reader = DriveReader()
    embeddings = GeminiEmbeddingsClient()
    kb = KnowledgeBase()

    any_folder_configured = False
    total_indexed = 0
    total_skipped = 0

    for destination, env_var in FOLDERS_TO_INDEX.items():
        folder_id = os.getenv(env_var)
        if not folder_id:
            print(f"⏭️  {env_var} no configurado — saltando destino '{destination}'.")
            continue

        any_folder_configured = True
        print(f"📂 Leyendo carpeta '{destination}'...")
        try:
            documents = reader.list_documents(folder_id)
        except RuntimeError as e:
            print(f"❌ {e}")
            continue

        print(f"   {len(documents)} documento(s) encontrados.")

        for doc in documents:
            doc_id = doc["id"]
            title = doc.get("name", "Sin título")
            modified_time = doc.get("modifiedTime")
            source_link = doc.get("webViewLink", "")

            if kb.get_modified_time(doc_id) == modified_time:
                total_skipped += 1
                continue

            try:
                text = reader.export_document_text(doc_id)
                excerpt = text[:MAX_CHARS_PER_DOC]
                embedding = await embeddings.embed(excerpt, task_type="RETRIEVAL_DOCUMENT")
                kb.add_or_update(doc_id, title, excerpt, embedding, source_link, modified_time)
                total_indexed += 1
                print(f"   ✅ Indexado: {title}")
            except RuntimeError as e:
                print(f"   ❌ Error con '{title}': {e}")

    if not any_folder_configured:
        print(
            "❌ No hay ninguna carpeta configurada (GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS / "
            "GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS). Nada que indexar."
        )
        sys.exit(1)

    print(f"\n✅ Listo: {total_indexed} indexado(s), {total_skipped} sin cambios (saltados).")


if __name__ == "__main__":
    asyncio.run(main())
