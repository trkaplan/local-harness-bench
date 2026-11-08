from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    created_at: str = ""
    tags: list[str] | None = None

    @staticmethod
    def new(id: int, title: str, tags: list[str] | None = None) -> "Task":
        return Task(id=id, title=title, done=False, created_at=datetime.now(timezone.utc).isoformat(), tags=tags or [])

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Task":
        return Task(id=int(d["id"]), title=d["title"], done=bool(d.get("done", False)), created_at=d.get("created_at", ""), tags=list(d.get("tags") or []))
