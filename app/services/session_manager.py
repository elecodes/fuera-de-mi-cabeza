import json
import uuid
from pathlib import Path
from app.models.session import EditorialSession


class SessionManager:
    """
    Gestor de persistencia local de sesiones editoriales en formato JSON.
    """

    def __init__(self, storage_dir: Path | str | None = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.storage_dir = Path(storage_dir) if storage_dir else base_dir / "data" / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, original_idea: str) -> EditorialSession:
        session_id = str(uuid.uuid4())[:8]
        session = EditorialSession(id=session_id, original_idea=original_idea)
        self.save_session(session)
        return session

    def save_session(self, session: EditorialSession) -> None:
        file_path = self.storage_dir / f"{session.id}.json"
        data = session.model_dump(mode="json")
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_session(self, session_id: str) -> EditorialSession | None:
        file_path = self.storage_dir / f"{session_id}.json"
        if not file_path.exists():
            return None
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return EditorialSession.model_validate(data)
