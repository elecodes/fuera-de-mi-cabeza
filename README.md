# Fuera de mi cabeza — Personal Editorial Agent (v0.7.0)

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
│   └── update_diagram_metadata.py # Actualizador automático de metadatos de versión y Git
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
El botón **"🔍 Auditar Voz Editorial"** analiza tu texto en tiempo real contra los 11 antipatrones de IA y la guía de estilo de [`data/editorial_profile.md`](file:///Users/elena/Developer/fuera-de-mi-cabeza/data/editorial_profile.md):
- **Voz Peninsular:** Redacción en **Español de España (castellano peninsular)** (*tú, tienes, has vivido*).
- **Varianza de Cadencia:** Oraciones cortas de énfasis combinadas espontáneamente con explicaciones matizadas.
- **Filtros Antipatrones IA:** Cero antítesis ("No es X, es Y"), cero introducciones vacías, cero frases triádicas, cero muletillas cautelosas, cero cierres circulares y cero emojis decorativos.

### 4. Aprendizaje Continuo & Memoria Editorial (`EditorialMemory`)
El agente aprende continuamente de tu feedback y ajusta su estilo post a post:
- **Persistencia en JSON (`data/editorial_memory.json`):** Almacena muletillas favoritas, palabras prohibidas, reglas de estilo/ritmo y formas de abrir tus notas (ej. *"Llevo bastante tiempo dándole vueltas a esta intuición: ..."*).
- **Panel Interactivo de Gestión de Voz:** En la UI web puedes añadir o eliminar reglas de estilo en tiempo real con un solo clic.
- **Optimización de Payload (65% Reducción):** Extrae las directrices clave de voz omitiendo bloques de texto repetitivos, permitiendo respuestas en menos de 1.5s en la API de Groq sin errores 413/429.

### 5. Salida en Texto Plano (sin JSON envolvente)
Note, Article y Revision ya no le piden al LLM que envuelva el borrador en un objeto JSON. El modelo devuelve el texto tal cual (Note y Revision) o título + contenido separados por los marcadores `===TITULO===` / `===CONTENIDO===` (Article), parseados por [`app/services/text_output.py`](app/services/text_output.py). Esto evita errores de escapado en textos largos y deja que el modelo escriba prosa sin tener que pensar en el formato de salida. `content_planner`, `idea_explorer`, `voice_auditor` y `argument_griller` siguen usando JSON, porque ahí sí devuelven varios campos estructurados (listas, arrays).

### 6. Exportar a Google Drive
El botón **"📤 Guardar en Google Drive"** (junto al de copiar al portapapeles) sube el borrador actual a una carpeta de tu Drive como **Google Doc nativo** (editable ahí mismo, con el título, negritas y listas ya aplicados). Es manual, no automático: solo se sube cuando pulsas el botón.

Usa una **cuenta de servicio** de Google, así que no hace falta iniciar sesión desde la app. Configuración, una sola vez:

1. **Crea un proyecto** en [Google Cloud Console](https://console.cloud.google.com/) (o usa uno existente).
2. **Activa la API de Google Drive**: en el buscador del proyecto, busca "Google Drive API" → *Habilitar*.
3. **Crea una cuenta de servicio**: *IAM y administración* → *Cuentas de servicio* → *Crear cuenta de servicio*. No necesita ningún rol de IAM especial.
4. **Genera una clave JSON**: dentro de la cuenta de servicio → pestaña *Claves* → *Agregar clave* → *Crear clave nueva* → tipo **JSON**. Se descarga un archivo — guárdalo en la raíz del repo, por ejemplo como `google-service-account.json` (ya está en `.gitignore`: nunca se sube al repo).
5. **Comparte tu carpeta de Drive** con la cuenta de servicio: abre la carpeta donde quieres guardar tus borradores → *Compartir* → pega el email de la cuenta de servicio (termina en `...gserviceaccount.com`, lo ves en la consola) → dale rol de **Editor**.
6. **Copia el ID de la carpeta**: es la parte de la URL después de `folders/` cuando tienes la carpeta abierta en Drive.
7. **Añade a tu `.env`**:
   ```
   GOOGLE_SERVICE_ACCOUNT_FILE=google-service-account.json
   GOOGLE_DRIVE_FOLDER_ID=el_id_que_copiaste
   ```
8. Reinicia el backend. Genera un borrador y pulsa "Guardar en Google Drive" — debería aparecer un enlace para abrir el documento.

Si algo falla (archivo de credenciales no encontrado, carpeta no compartida, permisos), el error real aparece debajo del botón — nunca se guarda nada en silencio.

