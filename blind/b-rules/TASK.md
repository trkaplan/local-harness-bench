Add a SQLite storage backend to the `todo` package and make it the default, keeping the JSON backend available.

Requirements:
1. New module `todo/sqlite_store.py` with class `SqliteStore(path)` exposing the same interface as `JsonStore`: `load() -> list[Task]`, `save(tasks)`, `next_id(tasks)`. Use only the standard library (`sqlite3`). Table name `tasks`, columns `id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, tags TEXT NOT NULL` where `tags` is a JSON-encoded list. `save()` must replace the full contents atomically (single transaction). `next_id` must be `max(id)+1` or 1 when empty, same as JsonStore.
2. `todo/storage.py` gains a factory `open_store(path: str | Path)` returning `JsonStore` when the path ends with `.json`, otherwise `SqliteStore`.
3. CLI: `--file` default becomes `~/.todo.db` (still overridable by the `TODO_FILE` env var); the CLI must use `open_store`, so `--file x.json` still works with JSON.
4. New CLI subcommand `migrate SRC DST` that copies all tasks from one store to the other (either direction, chosen by extension), preserving ids, done flags, created_at and tags, and prints `migrated N tasks`. Migrating into a non-empty destination must fail with exit code 1 and message `destination not empty` on stderr, without modifying it.
5. New `todo/service.py` method `TodoService.rename(task_id, new_title)` returning the updated Task, raising `KeyError` for unknown ids, and a CLI subcommand `rename ID TITLE` printing `renamed #ID`.
6. Add tests for the SQLite store, the factory, migrate and rename. All existing tests must keep passing. Update README.md to describe the new default and the migrate command.

Run the full test suite before you finish.
