from __future__ import annotations
from .models import Task
from .storage import JsonStore


class TodoService:
    def __init__(self, store: JsonStore):
        self.store = store

    def add(self, title: str, tags: list[str] | None = None) -> Task:
        tasks = self.store.load()
        t = Task.new(self.store.next_id(tasks), title, tags)
        tasks.append(t)
        self.store.save(tasks)
        return t

    def list(self, include_done: bool = False, tag: str | None = None) -> list[Task]:
        tasks = self.store.load()
        out = [t for t in tasks if include_done or not t.done]
        if tag:
            out = [t for t in out if tag in (t.tags or [])]
        return out

    def complete(self, task_id: int) -> Task:
        tasks = self.store.load()
        for t in tasks:
            if t.id == task_id:
                t.done = True
                self.store.save(tasks)
                return t
        raise KeyError(task_id)

    def remove(self, task_id: int) -> None:
        tasks = self.store.load()
        new = [t for t in tasks if t.id != task_id]
        if len(new) == len(tasks):
            raise KeyError(task_id)
        self.store.save(new)
