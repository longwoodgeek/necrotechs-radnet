"""Local RadNet BBS prototype with development posting. No sockets, accounts or shell execution."""
from pathlib import Path
import sqlite3
from contextlib import closing
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
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
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
        "Mode: LOCAL DEVELOPMENT / LOCAL POSTING ENABLED",
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
        return "CAPTAIN'S LOG\nLocal append-only archive; select 3 in the interactive terminal."
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
            output_fn("\nBOARDS:")
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
                output_fn(f"\n{safe_text(selected['title'])} // PAGE {page_num}")
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
                    output_fn(f"\n{safe_text(item['title'], 100)}")
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
            output_fn("\nBoard console closed.")
            return
        except BoardError as exc:
            output_fn(f"Board operation rejected: {exc}")

def display_log(record, output_fn):
    """Sanitize all archive text at the display boundary, including metadata."""
    data = record['data']
    receipt = data['receipt']
    lines = [
        'Original' if record['envelope']['kind'] == 'log.create' else 'Correction',
        f"Entry ID: {record['entry_id']}", f"Event ID: {record['id']}",
        f"Local receipt sequence: {record['received_seq']} (local ordering only)",
        f"Title: {data['title']}", f"Operator: {record['envelope']['author']} [UNVERIFIED]",
        data['body'], f"Claimed operator time: {data['claimed_time'] or 'not supplied'}",
        f"Claimed source: {data['time_source']}", f"Uncertainty: {data['uncertainty']}",
        f"Receipt clock: {receipt['time']} / {receipt['source']}",
        f"Receipt uncertainty: {receipt['uncertainty']}", f"Provenance: {data['provenance']}",
        f"Correction reason: {data.get('reason') or 'none'}",
    ]
    for line in lines:
        output_fn(safe_text(line, 4100))


def interactive_log(db_path, input_fn, output_fn):
    from .captains_log import CaptainsLog, LogError
    service = CaptainsLog(db_path)

    def ask(prompt, limit):
        value = input_fn(prompt)
        if len(value) > limit:
            raise LogError(f'Input exceeds {limit} characters')
        return value

    def fields():
        author = ask('Operator label (unverified, max 32): ', 32)
        title = ask('Title (max 100): ', 100)
        body = ask('Entry (one line, max 4000): ', 4000)
        claimed = ask('Claimed time (ISO 8601 with offset; blank = none): ', 64).strip()
        source = ask('Claimed time source (blank = not supplied): ', 200).strip()
        uncertainty = ask('Claimed time uncertainty (blank = unknown): ', 200).strip()
        return author, title, body, dict(claimed_time=claimed or None,
                                        time_source=source or 'not supplied',
                                        uncertainty=uncertainty or 'unknown')

    def pages(fetch):
        number = 1
        while True:
            items = fetch(number)
            output_fn(f'PAGE {number} // receipt order, not proof of occurrence time')
            if not items:
                output_fn('No matching log records.')
            for item in items:
                display_log(item, output_fn)
            command = ask('[>] Next [<] Previous [0] Return: ', 1).strip()
            if command == '0':
                return
            if command == '>' and len(items) == 10 and number < 10000:
                number += 1
            elif command == '<' and number > 1:
                number -= 1

    output_fn("CAPTAIN'S LOG // LOCAL ONLY // OPERATORS AND CLOCKS UNVERIFIED")
    output_fn('Corrections retain originals. Hashes are not signatures. No network.')
    while True:
        output_fn('[1] Browse [2] Create [3] History [4] Search all revisions [5] Export [6] Correct [0] Return')
        try:
            choice = ask('LOG:// > ', 1).strip()
            if choice == '0':
                return
            if choice == '1':
                pages(service.browse)
            elif choice == '2':
                author, title, body, metadata = fields()
                eid = service.create(author, title, body, **metadata)
                output_fn(f'Entry saved: {eid}')
            elif choice == '3':
                root = ask('Original entry ID (64 characters): ', 64).strip()
                pages(lambda number: service.history(root, number))
            elif choice == '4':
                query = ask('Search text (max 200): ', 200)
                pages(lambda number: service.search(query, number))
            elif choice == '5':
                target = ask('New export filename (never overwrites, max 1024): ', 1024)
                if not target.strip() or any(unicodedata.category(ch).startswith('C') for ch in target):
                    raise LogError('Invalid export filename')
                service.export(target)
                output_fn('Archive exported; journal retained.')
            elif choice == '6':
                root = ask('Original entry ID: ', 64).strip()
                previous = ask('Latest event ID from history (stale corrections rejected): ', 64).strip()
                author, title, body, metadata = fields()
                reason = ask('Correction reason (max 500): ', 500)
                eid = service.correct(root, previous, author, title, body, reason, **metadata)
                output_fn(f'Correction saved: {eid}')
            else:
                output_fn('Unknown selection.')
        except (EOFError, KeyboardInterrupt):
            output_fn('\nLog console closed.')
            return
        except LogError as exc:
            output_fn(f'Log operation rejected: {safe_text(exc)}')


def run(db_path, *, ansi=False, input_fn=input, output_fn=print):
    """Run an interactive local session; never executes OS commands."""
    output_fn(paint(BANNER, ansi))
    output_fn("RADNET BBS v0.4 // LOCAL DEVELOPMENT // LOCAL POSTING ENABLED")
    output_fn("AUTHORS UNVERIFIED // No authentication or authorization.")
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
        elif choice == "3":
            interactive_log(db_path, input_fn, output_fn)
        else:
            output_fn(paint(page(choice, db_path), ansi))


if __name__ == "__main__":
    run("radnet-dev.sqlite3", ansi=sys.stdout.isatty())
