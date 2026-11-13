import argparse
import json
import sqlite3
from .boot import render_boot
from .core import EventStore


def main():
    p = argparse.ArgumentParser(description="RadNet experimental local event journal")
    p.add_argument("--db", default="radnet-dev.sqlite3", help="local SQLite database")
    sub = p.add_subparsers(dest="command", required=True)
    add = sub.add_parser("post", help="append a local message")
    add.add_argument("author")
    add.add_argument("body")
    add.add_argument("--parent", action="append", default=[])
    sub.add_parser("list", help="list recent events")
    sub.add_parser("verify", help="check content hashes (not signatures)")
    sub.add_parser("boot", help="display the RadNet startup diagnostics")
    terminal = sub.add_parser("terminal", help="run local BBS terminal with local posting")
    terminal.add_argument("--plain", action="store_true", help="disable ANSI colors")
    args = p.parse_args()
    if args.command == "boot":
        print(render_boot(args.db))
        return
    if args.command == "terminal":
        import sys
        from .terminal import run
        run(args.db, ansi=sys.stdout.isatty() and not args.plain)
        return
    store = EventStore(args.db)
    try:
        if args.command == "post":
            print(store.append("message.create", args.author, args.body, args.parent))
        elif args.command == "list":
            print(json.dumps(store.list(), indent=2, ensure_ascii=False))
        elif args.command == "verify":
            bad = store.verify()
            print("Local content-hash check: " + ("PASS" if not bad else "FAIL"))
            if bad:
                print("\n".join(bad))
                raise SystemExit(1)
    finally:
        store.close()

if __name__ == "__main__":
    main()
