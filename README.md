# Fuera de mi cabeza — Personal Editorial Agent (MVP v0.1)

MVP de un editor personal en Python para el Substack **"Fuera de mi cabeza"** (tecnología, IA, aprendizaje y reflexiones sobre cómo convertir conocimiento en cosas reales).

El agente no escribe inmediatamente. Su objetivo principal es ayudarte a pensar, explorar qué querés decir realmente y estructurar el borrador manteniendo tu voz sin inventar experiencias personales.

---

## 🛠️ Flujo Principal Implementado

```
IDEA → EXPLORAR → PREGUNTAR → ESTRUCTURAR → BORRADOR (Note / Article) → FEEDBACK → REVISIÓN
```

---

## 🏗️ Estructura del Proyecto

```
fuera-de-mi-cabeza/
├── data/
│   ├── editorial_profile.md     # Perfil e identidad del autor
│   └── sessions/                # Persistencia local JSON de sesiones
├── app/
│   ├── main.py                  # Endpoints FastAPI y Web UI
│   ├── models/
│   │   ├── idea.py              # Modelos Pydantic para ideas
│   │   ├── analysis.py          # Modelo de análisis de la idea
│   │   ├── content_plan.py      # Modelo de plan de contenido
│   │   ├── draft.py             # Modelo de borrador (Note/Article)
│   │   └── session.py           # Modelo de sesión editorial
│   ├── services/
│   │   ├── idea_explorer.py     # Analiza la idea y hace preguntas
│   │   ├── content_planner.py   # Genera el plan de contenido
│   │   ├── draft_generator.py   # Redacta Notes o Artículos
│   │   ├── voice_editor.py      # Ajusta el texto según tu feedback
│   │   └── session_manager.py   # Guarda el estado de la sesión
│   ├── llm/
│   │   ├── client.py            # Protocol LLMClient
│   │   └── providers/           # Mock LLM y cliente HTTPX OpenAI-compatible
│   ├── memory/
│   │   └── editorial_memory.py  # Interfaz preparatoria para MVP v0.2
│   ├── prompts/                 # Templates Markdown para el LLM
│   └── web/
│       └── index.html           # Interfaz Web minimalista (cuaderno digital)
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
Navegá a **`http://localhost:8000`** en tu navegador para usar la interfaz estilo cuaderno digital.

### 3. Ejecutar los Tests
```bash
pytest
```

### 4. Demostraciones por CLI
```bash
# Probar solo el primer hito (IDEA -> ANALYSIS -> QUESTIONS)
python3 demo_idea_explorer.py

# Probar el flujo completo (IDEA -> PLAN -> DRAFT -> REVISIÓN)
python3 demo_full_workflow.py
```

---

## ⚙️ Configuración del Proveedor LLM y Voz Editorial

### 1. Voz Editorial
El agente está configurado para redactar y preguntar en **Español de España (castellano peninsular)** (*tú, tienes, has probado*), manteniendo un tono humano, reflexivo y sin clichés.

### 2. Configuración de Proveedores (Groq / OmniRoute / OpenAI)

Podés configurar el proveedor en tu archivo `.env`:

#### Opción A: Vía OmniRoute (Gateway de IA recomendado)
```env
LLM_PROVIDER=openai-compatible
LLM_BASE_URL=http://127.0.0.1:20128/v1
LLM_API_KEY=tu_omniroute_api_key
LLM_MODEL=groq/openai/gpt-oss-120b
LLM_FALLBACK_MODELS=groq/qwen/qwen3.6-27b
GROQ_API_KEY=tu_groq_api_key
```

#### Opción B: Groq Directo
```env
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=tu_groq_api_key
```

#### Opción C: Mock (para pruebas locales sin API key)
```env
LLM_PROVIDER=mock
```
