from pathlib import Path
from todo.storage import JsonStore
from todo.service import TodoService


def test_add_and_list(tmp_path: Path):
    svc = TodoService(JsonStore(tmp_path / "t.json"))
    svc.add("buy milk", ["home"])
    svc.add("ship release", ["work"])
    assert [t.title for t in svc.list()] == ["buy milk", "ship release"]
    assert [t.title for t in svc.list(tag="work")] == ["ship release"]


def test_complete_hides_from_default_list(tmp_path: Path):
    svc = TodoService(JsonStore(tmp_path / "t.json"))
    t = svc.add("a")
    svc.complete(t.id)
    assert svc.list() == []
    assert [x.id for x in svc.list(include_done=True)] == [t.id]


def test_cli_roundtrip(tmp_path: Path, capsys):
    from todo.cli import main
    f = str(tmp_path / "t.json")
    assert main(["--file", f, "add", "write tests", "--tag", "dev"]) == 0
    assert main(["--file", f, "list"]) == 0
    out = capsys.readouterr().out
    assert "#1 write tests [dev]" in out
