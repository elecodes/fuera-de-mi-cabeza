# Fuera de mi cabeza — Personal Editorial Agent (v0.4.1)

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
│   ├── editorial_profile.md     # Perfil e identidad del autor, reglas de ritmo y antipatrones IA
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
│   │   ├── idea_explorer.py     # Analiza ideas, desglosa pensamientos y sintetiza arcos
│   │   ├── content_planner.py   # Genera el plan según el arco narrativo elegido
│   │   ├── draft_generator.py   # Redacta Substack Notes o Artículos
│   │   ├── voice_auditor.py     # Audita la naturalidad y antipatrones de IA (editorial_profile.md)
│   │   ├── voice_editor.py      # Ajusta el texto según tu feedback
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
Puedes ingresar notas sueltas, viñetas o fragmentos de ideas. El agente desglosa tus pensamientos y te ofrece 2–3 **Arcos Narrativos** interactivos para elegir cómo quieres ordenar y conectar tus ideas antes de planificar.

### 2. Edición Directa & Copiado al Portapapeles
En el cuaderno web (`index.html`), puedes hacer clic y editar directamente el borrador generado (`contenteditable`). Un botón dedicado de **"📋 Copiar borrador al portapapeles"** te permite llevar el texto listo a Substack.

### 3. Auditoría de Voz Editorial y Filtros Anti-IA
El botón **"🔍 Auditar Voz Editorial"** analiza tu texto en tiempo real contra los 11 antipatrones de IA y la guía de estilo de [`data/editorial_profile.md`](file:///Users/elena/Developer/fuera-de-mi-cabeza/data/editorial_profile.md):
- **Voz Peninsular:** Redacción en **Español de España (castellano peninsular)** (*tú, tienes, has vivido*).
- **Varianza de Cadencia:** Oraciones cortas de énfasis combinadas espontáneamente con explicaciones matizadas.
- **Filtros Antipatrones IA:** Cero antítesis ("No es X, es Y"), cero introducciones vacías, cero frases triádicas, cero muletillas cautelosas, cero cierres circulares y cero emojis decorativos.
