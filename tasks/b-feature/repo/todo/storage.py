"""JSON file storage. The whole list is rewritten on every change."""
from __future__ import annotations
import json
from pathlib import Path
from .models import Task


class JsonStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text() or "[]")
        return [Task.from_dict(d) for d in data]

    def save(self, tasks: list[Task]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([t.to_dict() for t in tasks], indent=2))

    def next_id(self, tasks: list[Task]) -> int:
        return (max((t.id for t in tasks), default=0) + 1)
