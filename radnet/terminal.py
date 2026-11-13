"""Local, read-only RadNet BBS prototype. No sockets, accounts or shell execution."""
from pathlib import Path
import sqlite3
import sys
import unicodedata

BANNER = """+----------------------------------------------+
|          N E C R O T E C H S                 |
|                 R A D N E T                  |
|           THE NETWORK REMEMBERS              |
+----------------------------------------------+"""

MENU = """[1] MESSAGE BOARDS       [2] STATION STATUS
[3] CAPTAIN'S LOG        [4] COMMUNITY RESOURCES
[5] NETWORK DIRECTORY    [6] EMERGENCY INFORMATION
[0] DISCONNECT"""

# ANSI is optional; plain mode remains readable on minimal terminals.
GREEN = "\x1b[32m"
RESET = "\x1b[0m"


def paint(message, ansi=False):
    return f"{GREEN}{message}{RESET}" if ansi else message


def safe_text(value, limit=180):
    # Strip control/format characters, including ANSI ESC, from untrusted event text.
    cleaned = ''.join(ch if unicodedata.category(ch)[0] != 'C' else ' ' for ch in str(value))
    return cleaned[:limit]


def read_events(db_path, limit=20):
    """Read a pre-existing journal without creating or modifying it."""
    path = Path(db_path)
    if not path.is_file():
        return [], "No local journal found. Nothing has been created."
    try:
        with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as db:
            rows = db.execute(
                "SELECT id, envelope FROM events ORDER BY received_seq DESC LIMIT ?",
                (limit,),
            ).fetchall()
        import json
        return [(eid, json.loads(envelope)) for eid, envelope in rows], None
    except (sqlite3.Error, OSError, ValueError, TypeError) as exc:
        return [], f"Journal unavailable ({type(exc).__name__})."


def station_status(db_path):
    events, error = read_events(db_path)
    return "\n".join([
        "STATION STATUS",
        "Mode: LOCAL / READ-ONLY DEVELOPMENT",
        "Transport: NOT CONNECTED",
        "Identity: NOT VERIFIED",
        "Federation: NOT IMPLEMENTED",
        "Emergency dispatch: NOT AVAILABLE",
        error or f"Journal: readable; showing up to {len(events)} recent events",
    ])


def message_boards(db_path):
    events, error = read_events(db_path)
    if error:
        return "MESSAGE BOARDS\n" + error
    messages = [(eid, item) for eid, item in events if item.get("kind") == "message.create"]
    if not messages:
        return "MESSAGE BOARDS\nNo local messages yet."
    lines = ["MESSAGE BOARDS — RECENT LOCAL EVENTS (UNVERIFIED AUTHORS)"]
    for eid, item in messages:
        author = str(item.get("author", "unknown")).replace("\n", " ")[:32]
        body = str(item.get("body", "")).replace("\r", " ").replace("\n", " ")[:180]
        lines.append(f"[{str(item.get('local_seq', '?'))}] {author}: {body}")
        lines.append(f"    event {eid[:16]}...")
    return "\n".join(lines)


def page(choice, db_path):
    if choice == "1":
        return message_boards(db_path)
    if choice == "2":
        return station_status(db_path)
    if choice == "3":
        return "CAPTAIN'S LOG\nComing soon. Local journal events are visible under Message Boards."
    if choice == "4":
        return "COMMUNITY RESOURCES\nComing soon. No external resources have been verified."
    if choice == "5":
        return "NETWORK DIRECTORY\nNot connected. No peers or routes are being discovered."
    if choice == "6":
        return ("EMERGENCY INFORMATION\n"
                "PROTOTYPE ONLY — NOT AN EMERGENCY SERVICE.\n"
                "This terminal cannot request, confirm, or dispatch assistance.\n"
                "For immediate danger, use your local emergency services.")
    return "Unknown command. Choose 0 through 6."


def run(db_path, *, ansi=False, input_fn=input, output_fn=print):
    """Run an interactive local session; never executes OS commands."""
    output_fn(paint(BANNER, ansi))
    output_fn("RADNET BBS v0.2 // LOCAL DEVELOPMENT // GUEST READ-ONLY")
    output_fn("This system is experimental. No network or emergency dispatch.")
    while True:
        output_fn("")
        output_fn(paint(MENU, ansi))
        try:
            choice = input_fn("RADNET:// SELECT > ").strip()
        except (EOFError, KeyboardInterrupt):
            output_fn("\nConnection closed.")
            return
        if choice == "0":
            output_fn("Disconnecting. THE NETWORK REMEMBERS.")
            return
        output_fn("")
        output_fn(paint(page(choice, db_path), ansi))


if __name__ == "__main__":
    run("radnet-dev.sqlite3", ansi=sys.stdout.isatty())
