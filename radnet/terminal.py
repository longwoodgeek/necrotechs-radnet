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



def interactive_boards(db_path, input_fn, output_fn, ansi=False):
    """Local development board browser and posting console."""
    from .boards import Boards, BoardError
    service = Boards(db_path)
    output_fn("LOCAL BOARD CONSOLE // AUTHORS UNVERIFIED // NO NETWORK")
    while True:
        try:
            boards = service.boards()
            output_fn("\\nBOARDS:")
            for number, board in enumerate(boards, 1):
                output_fn(f"[{number}] {safe_text(board['title'], 100)}")
            output_fn("[N] New board  [0] Return")
            choice = input_fn("BOARD:// > ").strip().lower()
            if choice == "0":
                return
            if choice == "n":
                author = input_fn("Author (unverified): ")
                title = input_fn("New board title: ")
                eid = service.create_board(title, author)
                output_fn(f"Board created: {eid[:16]}...")
                continue
            if not choice.isdecimal() or not 1 <= int(choice) <= len(boards):
                output_fn("Unknown selection.")
                continue
            selected = boards[int(choice) - 1]
            page_num = 1
            while True:
                items = service.messages(selected["id"], page_num)
                output_fn(f"\\n{safe_text(selected['title'])} // PAGE {page_num}")
                for number, item in enumerate(items, 1):
                    output_fn(f"[{number}] {safe_text(item['title'], 100)} — {safe_text(item['author'], 32)}")
                output_fn("[N] New post  [>] Next  [<] Previous  [0] Boards")
                command = input_fn("POSTS:// > ").strip().lower()
                if command == "0":
                    break
                if command == ">" and len(items) == 10:
                    page_num += 1
                elif command == "<" and page_num > 1:
                    page_num -= 1
                elif command == "n":
                    author = input_fn("Author (unverified): ")
                    title = input_fn("Title: ")
                    body = input_fn("Message (one line, max 4000 chars): ")
                    eid = service.post(selected["id"], author, title, body)
                    output_fn(f"Posted locally: {eid[:16]}...")
                    page_num = 1
                elif command.isdecimal() and 1 <= int(command) <= len(items):
                    item = items[int(command) - 1]
                    output_fn(f"\\n{safe_text(item['title'], 100)}")
                    output_fn(f"By {safe_text(item['author'], 32)} [UNVERIFIED]")
                    output_fn(safe_text(item["body"], 4000))
                    if input_fn("Reply? [y/N] ").strip().lower() == "y":
                        author = input_fn("Author (unverified): ")
                        body = input_fn("Reply (one line): ")
                        service.post(selected["id"], author, "Re: " + safe_text(item["title"], 95), body, parent=item["id"])
                        output_fn("Reply saved locally.")
                else:
                    output_fn("Unknown selection.")
        except (EOFError, KeyboardInterrupt):
            output_fn("\\nBoard console closed.")
            return
        except BoardError as exc:
            output_fn(f"Board operation rejected: {exc}")

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
        if choice == "1":
            interactive_boards(db_path, input_fn, output_fn, ansi)
        else:
            output_fn(paint(page(choice, db_path), ansi))


if __name__ == "__main__":
    run("radnet-dev.sqlite3", ansi=sys.stdout.isatty())
