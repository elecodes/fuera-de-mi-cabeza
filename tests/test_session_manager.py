from pathlib import Path
from app.services.session_manager import SessionManager


def test_session_manager_crud(tmp_path: Path):
    manager = SessionManager(storage_dir=tmp_path)

    # 1. Crear sesión
    session = manager.create_session(original_idea="Idea de prueba")
    assert session.id is not None
    assert session.original_idea == "Idea de prueba"

    # 2. Recuperar sesión
    retrieved = manager.get_session(session.id)
    assert retrieved is not None
    assert retrieved.id == session.id
    assert retrieved.original_idea == "Idea de prueba"

    # 3. Actualizar sesión
    session.user_answers = ["Respuesta 1"]
    manager.save_session(session)

    updated = manager.get_session(session.id)
    assert updated is not None
    assert updated.user_answers == ["Respuesta 1"]


def test_session_manager_non_existent(tmp_path: Path):
    manager = SessionManager(storage_dir=tmp_path)
    assert manager.get_session("invalid-id") is None
