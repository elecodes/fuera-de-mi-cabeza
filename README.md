# Fuera de mi cabeza — Personal Editorial Agent (v0.9.0)

Editor personal en Python para el Substack **"Fuera de mi cabeza"** (tecnología, IA, aprendizaje y reflexiones sobre cómo convertir conocimiento en cosas reales).

El agente no escribe inmediatamente. Su objetivo principal es ayudarte a pensar, explorar y conectar notas sueltas o ideas en bruto, ordenarlas mediante **Arcos Narrativos** interactivos y estructurar borradores (Substack Notes o Posts) manteniendo tu voz sin inventar experiencias personales.

---

## 🛠️ Flujo Principal Implementado

```
BRAIN DUMP (Notas/Ideas) → ARCOS NARRATIVOS (Selección) → PREGUNTAR → PLAN → BORRADOR (Note/Post) → EDICIÓN DIRECTA / AUDITORÍA DE VOZ → REVISIÓN
```

---

## 🏗️ Estructura del Proyecto

```
fuera-de-mi-cabeza/
├── SOUL.md                      # Constitución del agente y arquitectura de comportamiento
├── CHANGELOG.md                 # Historial de cambios y versiones (Keep a Changelog)
├── docs/
│   ├── adr/                     # Architecture Decision Records (MADR)
│   └── architecture/            # Diagramas interactivos de arquitectura de Archify
├── scripts/
│   ├── update_diagram_metadata.py # Actualizador automático de metadatos de versión y Git
│   ├── authorize_google_drive.py  # Autorización OAuth de Google Drive (una sola vez)
│   └── ingest_published_drive_docs.py # Indexa lo publicado en Drive para el RAG ligero
├── data/
│   ├── voice_guide.md           # Guía de voz, hábitos de escritura, ritmo y antipatrones a evitar
│   ├── voice_samples.md         # Muestras reales de texto del autor (gitignored por privacidad)
│   ├── editorial_profile.md     # Perfil e identidad del autor
│   ├── editorial_memory.json    # Persistencia local de reglas y preferencias de estilo
│   └── sessions/                # Persistencia local JSON de sesiones

├── app/
│   ├── main.py                  # Endpoints FastAPI, Web UI y rutas de diagramas
│   ├── models/
│   │   ├── idea.py              # Modelos Pydantic para ideas y brain dumps
│   │   ├── analysis.py          # Modelo de análisis y Arcos Narrativos
│   │   ├── content_plan.py      # Modelo de plan de contenido
│   │   ├── draft.py             # Modelo de borrador (Substack Note / Article)
│   │   ├── voice_audit.py       # Modelo de reporte de auditoría editorial
│   │   └── session.py           # Modelo de sesión editorial
│   ├── services/
│   │   ├── voice_profile.py     # Carga centralizada de voz (voice_guide, voice_samples y memory)
│   │   ├── text_output.py       # Parseo de salida en texto plano del LLM (título + contenido, sin JSON)
│   │   ├── idea_explorer.py     # Analiza ideas, desglosa pensamientos y sintetiza arcos
│   │   ├── content_planner.py   # Genera el plan según el arco narrativo elegido
│   │   ├── draft_generator.py   # Redacta Substack Notes o Artículos
│   │   ├── voice_auditor.py     # Audita la naturalidad y antipatrones de IA
│   │   ├── voice_editor.py      # Ajusta el texto según tu feedback
│   │   ├── drive_uploader.py    # Exporta el borrador a Google Drive como Google Doc nativo
│   │   ├── google_drive_auth.py # Carga y renovación de credenciales OAuth de Drive (compartido)
│   │   ├── drive_reader.py      # Lee y exporta el texto de Google Docs de una carpeta de Drive
│   │   ├── embeddings_client.py # Cliente de la API de embeddings de Gemini
│   │   ├── knowledge_base.py    # Almacén local de piezas publicadas + búsqueda por similitud
│   │   ├── tracer.py            # Observabilidad ligera: registra cada llamada al LLM
│   │   └── session_manager.py   # Guarda el estado de la sesión

│   ├── llm/
│   │   ├── client.py            # Protocol LLMClient
│   │   └── providers/           # Mock LLM y cliente HTTPX OpenAI-compatible
│   ├── memory/
│   │   └── editorial_memory.py  # Memoria editorial y preferencias de estilo
│   ├── prompts/                 # Templates Markdown para el LLM
│   └── web/
│       └── index.html           # Interfaz Web (cuaderno digital con edición directa y copiado)
├── tests/                       # Suite completa de tests unitarios e integración
├── pyproject.toml
└── README.md
```

---

## 🚀 Cómo ejecutar la aplicación

### 1. Requisitos e Instalación
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev] uvicorn
```

### 2. Ejecutar la Web UI (FastAPI + Uvicorn)
```bash
uvicorn app.main:app --reload
```
Navega a **`http://localhost:8000`** en tu navegador para usar la interfaz de cuaderno digital.

### 3. Ejecutar los Tests
```bash
python3 -m pytest
```

---

## ⚙️ Características Clave & Voz Editorial

### 1. Brain Dumps & Arcos Narrativos
Puedes ingresar notas sueltas, viñetas o fragmentos de ideas. El agente desglosa tus pensamientos y te ofrece 2–3 **Arcos Narrativos** interactivos para elegir cómo quieres ordenar y conectar tus ideas antes de planificar. Las preguntas de profundización están ancladas a escena y detalle concreto (un momento, un lugar, una frase textual, una cifra), no a temas generales, y no repreguntan por un dato que ya diste en la idea original.

### 2. Edición Directa & Copiado al Portapapeles
En el cuaderno web (`index.html`), puedes hacer clic y editar directamente el borrador generado (`contenteditable`). Un botón dedicado de **"📋 Copiar borrador al portapapeles"** te permite llevar el texto listo a Substack.

### 3. Auditoría de Voz Editorial y Filtros Anti-IA
El botón **"🔍 Auditar Voz Editorial"** analiza tu texto en tiempo real contra los 11 antipatrones de IA y la guía de estilo de `data/editorial_profile.md`:
- **Voz Peninsular:** Redacción en **Español de España (castellano peninsular)** (*tú, tienes, has vivido*).
- **Varianza de Cadencia:** Oraciones cortas de énfasis combinadas espontáneamente con explicaciones matizadas.
- **Filtros Antipatrones IA:** Cero antítesis ("No es X, es Y"), cero introducciones vacías, cero frases triádicas, cero muletillas cautelosas, cero cierres circulares y cero emojis decorativos.

### 4. Aprendizaje Continuo & Memoria Editorial (`EditorialMemory`)
El agente aprende continuamente de tu feedback y ajusta su estilo post a post:
- **Persistencia en JSON (`data/editorial_memory.json`):** Almacena muletillas favoritas, palabras prohibidas, reglas de estilo/ritmo y formas de abrir tus notas (ej. *"Llevo bastante tiempo dándole vueltas a esta intuición: ..."*).
- **Panel Interactivo de Gestión de Voz:** En la UI web puedes añadir o eliminar reglas de estilo en tiempo real con un solo clic.
- **Optimización de Payload (65% Reducción):** Extrae las directrices clave de voz omitiendo bloques de texto repetitivos, permitiendo respuestas en menos de 1.5s en la API de Groq sin errores 413/429.

### 5. Salida en Texto Plano (sin JSON envolvente)
Note, Article y Revision ya no le piden al LLM que envuelva el borrador en un objeto JSON. El modelo devuelve el texto tal cual (Note y Revision) o título + contenido separados por los marcadores `===TITULO===` / `===CONTENIDO===` (Article), parseados por `app/services/text_output.py`. Esto evita errores de escapado en textos largos y deja que el modelo escriba prosa sin tener que pensar en el formato de salida. `content_planner`, `idea_explorer`, `voice_auditor` y `argument_griller` siguen usando JSON, porque ahí sí devuelven varios campos estructurados (listas, arrays).

### 6. Exportar a Google Drive
El botón **"📤 Guardar en Google Drive"** (junto al de copiar al portapapeles) sube el borrador actual a una carpeta de tu Drive como **Google Doc nativo** (editable ahí mismo, con el título, negritas y listas ya aplicados). Es manual, no automático: solo se sube cuando pulsas el botón.

Puedes elegir el destino en un desplegable junto al botón: **Borradores**, **Notes publicados** o **Posts publicados**, cada uno una carpeta de Drive distinta (ver ADR 0017).

Usa **OAuth como tú misma** (no una cuenta de servicio: para una cuenta de Gmail normal, sin Google Workspace, las cuentas de servicio tienen 0 GB de cuota propia y no pueden crear archivos — ver ADR 0016). Configuración, una sola vez:

1. **Crea un proyecto** en [Google Cloud Console](https://console.cloud.google.com/) (o usa uno existente).
2. **Activa la API de Google Drive**: en el buscador del proyecto, busca "Google Drive API" → *Habilitar*.
3. **Configura la pantalla de consentimiento OAuth**: *APIs y servicios* → *Pantalla de consentimiento OAuth* → tipo **Externo** → rellena lo mínimo obligatorio → en la sección **"Usuarios de prueba"**, añade tu propia cuenta de Gmail. **Este paso es obligatorio incluso siendo tú la única usuaria** — si lo saltas, la autorización falla con `Error 403: access_denied` ("no ha completado el proceso de verificación de Google").
4. **Crea un Client ID de OAuth**: *APIs y servicios* → *Credenciales* → *Crear credenciales* → *ID de cliente de OAuth* → tipo **"App de escritorio"** (no "Aplicación web": ese tipo exige una URL de redirección fija y falla con `Error 400: redirect_uri_mismatch`, porque el script usa un puerto local que cambia cada vez).
5. **Descarga el JSON del cliente**: en la lista de credenciales, junto al Client ID que acabas de crear, pulsa el icono de descarga. Guárdalo en la raíz del repo, por ejemplo como `google-oauth-client-secret.json` (ya está en `.gitignore`).
6. **Crea (o elige) las carpetas de Drive** que quieras usar como destino — cada una es tuya, no hace falta compartir ninguna con nadie. Para cada una, copia su ID: es la parte de la URL después de `folders/`. No hace falta configurar las tres: puedes empezar solo con "Borradores" e ir añadiendo las demás cuando las necesites.
7. **Añade a tu `.env`**:
   ```
   GOOGLE_OAUTH_CLIENT_SECRET_FILE=google-oauth-client-secret.json
   GOOGLE_OAUTH_TOKEN_FILE=google-oauth-token.json
   GOOGLE_DRIVE_FOLDER_BORRADORES=el_id_de_esa_carpeta
   GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS=el_id_de_esa_carpeta
   GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS=el_id_de_esa_carpeta
   ```
8. **Autoriza el acceso, una sola vez**:
   ```bash
   python3 scripts/authorize_google_drive.py
   ```
   Se abre tu navegador, inicias sesión con tu cuenta de Google, aceptas el acceso a Drive, y se guarda un archivo de token (`google-oauth-token.json`, también en `.gitignore`) que el backend renueva solo a partir de ahí.
9. Reinicia el backend. Genera un borrador, elige el destino en el desplegable y pulsa "Guardar en Google Drive" — debería aparecer un enlace para abrir el documento.

Si algo falla (token caducado, carpeta equivocada, un destino sin configurar, permisos), el error real aparece debajo del botón — nunca se guarda nada en silencio.

### 7. Catálogo publicado (RAG ligero)
Al explorar una idea nueva, la app avisa si ya escribiste algo parecido: compara tu idea por *significado* (no por palabras) contra tus Notes y Posts ya publicados, y muestra un aviso **"📚 Ya escribiste algo parecido"** con enlaces, si encuentra algo suficientemente similar. No mete ese contenido antiguo dentro del prompt del LLM — es solo un aviso informativo para ti, para que decidas si conectar con esa pieza, evitar repetirte, o seguir igualmente (ver ADR 0020).

Nada de bases de datos vectoriales: un JSON local (`data/knowledge_base.json`, gitignored) con cada pieza y su "embedding" (huella semántica), comparados por similitud de coseno en Python — de sobra para un catálogo personal.

Configuración, una sola vez:

1. **Consigue una clave de la API de Gemini**: en [Google AI Studio](https://aistudio.google.com/apikey), crea una clave (tiene tier gratuito).
2. **Añade a tu `.env`**:
   ```
   GEMINI_API_KEY=tu_clave
   ```
3. **Indexa lo que ya tienes publicado** (usa las carpetas de Drive de `GOOGLE_DRIVE_FOLDER_NOTES_PUBLICADOS` / `GOOGLE_DRIVE_FOLDER_POSTS_PUBLICADOS` que ya configuraste en la sección anterior — no hace falta mover ni copiar nada):
   ```bash
   python3 scripts/ingest_published_drive_docs.py
   ```
   Solo indexa lo que haya cambiado desde la última vez que lo corriste, así que puedes volver a ejecutarlo cuando quieras refrescar el catálogo (por ejemplo, después de publicar algo nuevo) sin volver a gastar cuota en lo que no ha cambiado.
4. Reinicia el backend. Al explorar una idea nueva, si hay algo parecido ya publicado, debería aparecer el aviso con el enlace.

Si `GEMINI_API_KEY` no está configurado, o el catálogo está vacío, el aviso simplemente no aparece — no bloquea ni interrumpe el resto del flujo.

### 8. Observabilidad
El botón **"🔬 Observabilidad"** (arriba a la derecha) abre un panel con las últimas llamadas al LLM: qué paso del pipeline la hizo (`idea_explorer.analyze`, `draft_generator.generate_note`, etc.), cuánto tardó, si falló, y el prompt y la respuesta completos de cada una. Pensado para depurar "por qué ha salido así este borrador" sin tener que leer los prompts a mano, como hemos hecho muchas veces en el desarrollo de este proyecto.

No hace falta configurar nada — funciona automáticamente desde el primer arranque. Se guarda en `data/traces.jsonl` (gitignored, solo local), que conserva como mucho las 300 llamadas más recientes.

Se evaluó adoptar un framework de orquestación (Genkit) para esto, pero se descartó por ahora — ver ADR 0024 y ADR 0025 para el razonamiento completo.
