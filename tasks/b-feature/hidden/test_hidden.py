import json, sqlite3
from pathlib import Path
import pytest
from todo.models import Task
from todo.storage import JsonStore, open_store
from todo.sqlite_store import SqliteStore
from todo.service import TodoService
from todo.cli import main


def test_sqlite_roundtrip(tmp_path):
    s = SqliteStore(tmp_path / "t.db")
    assert s.load() == []
    assert s.next_id([]) == 1
    t1 = Task.new(1, "a", ["x", "y"]); t2 = Task(id=7, title="b", done=True, created_at="2026-01-01T00:00:00+00:00", tags=[])
    s.save([t1, t2])
    got = s.load()
    assert sorted(t.id for t in got) == [1, 7]
    b = next(t for t in got if t.id == 7)
    assert b.done is True and b.created_at == "2026-01-01T00:00:00+00:00" and b.tags == []
    a = next(t for t in got if t.id == 1)
    assert a.tags == ["x", "y"]
    assert s.next_id(got) == 8


def test_sqlite_schema(tmp_path):
    p = tmp_path / "t.db"
    SqliteStore(p).save([Task.new(1, "a")])
    con = sqlite3.connect(p)
    cols = [r[1] for r in con.execute("PRAGMA table_info(tasks)")]
    assert cols == ["id", "title", "done", "created_at", "tags"]
    tags = con.execute("SELECT tags FROM tasks WHERE id=1").fetchone()[0]
    assert json.loads(tags) == []


def test_save_replaces_contents(tmp_path):
    s = SqliteStore(tmp_path / "t.db")
    s.save([Task.new(1, "a"), Task.new(2, "b")])
    s.save([Task.new(2, "b")])
    assert [t.id for t in s.load()] == [2]


def test_factory(tmp_path):
    assert isinstance(open_store(tmp_path / "x.json"), JsonStore)
    assert isinstance(open_store(str(tmp_path / "x.db")), SqliteStore)
    assert isinstance(open_store(tmp_path / "x.sqlite"), SqliteStore)


def test_cli_default_db(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path)); monkeypatch.delenv("TODO_FILE", raising=False)
    assert main(["add", "hello"]) == 0
    assert (tmp_path / ".todo.db").exists()
    assert not (tmp_path / ".todo.json").exists()


def test_cli_json_still_works(tmp_path, capsys):
    f = str(tmp_path / "t.json")
    assert main(["--file", f, "add", "j"]) == 0
    assert json.loads(Path(f).read_text())[0]["title"] == "j"


def test_migrate_json_to_sqlite(tmp_path, capsys):
    src = tmp_path / "s.json"; dst = tmp_path / "d.db"
    JsonStore(src).save([Task(id=3, title="z", done=True, created_at="2026-02-02T00:00:00+00:00", tags=["q"]), Task.new(5, "w")])
    assert main(["migrate", str(src), str(dst)]) == 0
    assert "migrated 2 tasks" in capsys.readouterr().out
    got = {t.id: t for t in SqliteStore(dst).load()}
    assert set(got) == {3, 5} and got[3].done and got[3].tags == ["q"] and got[3].created_at == "2026-02-02T00:00:00+00:00"


def test_migrate_sqlite_to_json(tmp_path, capsys):
    src = tmp_path / "s.db"; dst = tmp_path / "d.json"
    SqliteStore(src).save([Task.new(1, "a", ["t"])])
    assert main(["migrate", str(src), str(dst)]) == 0
    assert JsonStore(dst).load()[0].tags == ["t"]


def test_migrate_refuses_nonempty(tmp_path, capsys):
    src = tmp_path / "s.json"; dst = tmp_path / "d.db"
    JsonStore(src).save([Task.new(1, "a")])
    SqliteStore(dst).save([Task.new(9, "keep")])
    assert main(["migrate", str(src), str(dst)]) == 1
    assert "destination not empty" in capsys.readouterr().err
    assert [t.id for t in SqliteStore(dst).load()] == [9]


def test_rename_service_and_cli(tmp_path, capsys):
    svc = TodoService(SqliteStore(tmp_path / "t.db"))
    t = svc.add("old")
    assert svc.rename(t.id, "new").title == "new"
    assert svc.list()[0].title == "new"
    with pytest.raises(KeyError):
        svc.rename(999, "x")
    f = str(tmp_path / "c.db")
    main(["--file", f, "add", "a"])
    assert main(["--file", f, "rename", "1", "b"]) == 0
    assert "renamed #1" in capsys.readouterr().out
    assert main(["--file", f, "rename", "42", "b"]) == 1


def test_existing_cli_still_works(tmp_path, capsys):
    f = str(tmp_path / "t.db")
    assert main(["--file", f, "add", "write tests", "--tag", "dev"]) == 0
    assert main(["--file", f, "list"]) == 0
    assert "#1 write tests [dev]" in capsys.readouterr().out
    assert main(["--file", f, "done", "1"]) == 0
    assert main(["--file", f, "rm", "1"]) == 0
