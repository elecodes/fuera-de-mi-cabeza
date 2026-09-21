#!/usr/bin/env python3
"""
Script de automatización para actualizar dinámicamente los metadatos de versión,
fecha y commit de Git en los diagramas de Archify (docs/architecture/).
"""
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs" / "architecture"


def get_git_commit() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "latest"


def get_app_version() -> str:
    pyproject = ROOT_DIR / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return f"v{match.group(1)}"
    return "v0.3.0"


def update_diagram_file(file_path: Path, version: str, date_str: str, commit_hash: str):
    if not file_path.exists():
        return

    content = file_path.read_text(encoding="utf-8")

    # Reemplazar versión, fecha y commit en las etiquetas span del header
    pattern = r'(<span style="color: var\(--accent-blue\);">)[^<]+(</span>\s*•\s*<span style="color: var\(--accent-green\);">)[^<]+(</span>\s*•\s*<span style="color: var\(--accent-purple\); font-family: monospace;">)git:[^<]+(</span>)'
    replacement = rf'\g<1>{version}\g<2>{date_str}\g<3>git:{commit_hash}\g<4>'
    updated_content = re.sub(pattern, replacement, content)

    # Si no hubo reemplazo regex, hacer una sustitución limpia
    file_path.write_text(updated_content, encoding="utf-8")
    print(f"✅ Updated diagram metadata in {file_path.name}: {version} | {date_str} | git:{commit_hash}")


def main():
    commit = get_git_commit()
    version = get_app_version()
    date_str = datetime.now().strftime("%Y-%m-%d")

    arch_file = DOCS_DIR / "archify_architecture.html"
    seq_file = DOCS_DIR / "archify_sequence_flow.html"

    update_diagram_file(arch_file, version, date_str, commit)
    update_diagram_file(seq_file, version, date_str, commit)


if __name__ == "__main__":
    main()
