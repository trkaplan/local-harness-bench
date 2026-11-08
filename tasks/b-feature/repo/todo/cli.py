from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from .storage import JsonStore
from .service import TodoService


def default_path() -> Path:
    return Path(os.environ.get("TODO_FILE", Path.home() / ".todo.json"))


def build_service(args) -> TodoService:
    return TodoService(JsonStore(Path(args.file)))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="todo")
    p.add_argument("--file", default=str(default_path()), help="storage path")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("title"); a.add_argument("--tag", action="append", default=[])
    l = sub.add_parser("list"); l.add_argument("--all", action="store_true"); l.add_argument("--tag")
    d = sub.add_parser("done"); d.add_argument("id", type=int)
    r = sub.add_parser("rm"); r.add_argument("id", type=int)
    args = p.parse_args(argv)
    svc = build_service(args)
    if args.cmd == "add":
        t = svc.add(args.title, args.tag)
        print(f"added #{t.id}: {t.title}")
    elif args.cmd == "list":
        for t in svc.list(include_done=args.all, tag=args.tag):
            mark = "x" if t.done else " "
            tags = (" [" + ",".join(t.tags) + "]") if t.tags else ""
            print(f"[{mark}] #{t.id} {t.title}{tags}")
    elif args.cmd == "done":
        try:
            t = svc.complete(args.id)
        except KeyError:
            print(f"no task #{args.id}", file=sys.stderr); return 1
        print(f"done #{t.id}")
    elif args.cmd == "rm":
        try:
            svc.remove(args.id)
        except KeyError:
            print(f"no task #{args.id}", file=sys.stderr); return 1
        print(f"removed #{args.id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
