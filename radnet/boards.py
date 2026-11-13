"""Local bounded message-board service. Authors are unverified."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from .core import EventStore

class BoardError(ValueError):
    pass

def bounded(value, name, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise BoardError(f"{name} must be 1..{limit} characters")
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in value) or "\x7f" in value:
        raise BoardError(f"{name} contains control characters")
    return value.strip()

class Boards:
    def __init__(self, path):
        self.path = Path(path)

    def events(self):
        if not self.path.is_file():
            return []
        try:
            with closing(sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
                rows = db.execute("SELECT id,envelope FROM events ORDER BY received_seq").fetchall()
            return [(eid, json.loads(data)) for eid, data in rows]
        except (sqlite3.Error, OSError, ValueError) as exc:
            raise BoardError("Journal unavailable") from exc

    def boards(self):
        result = []
        for eid, event in self.events():
            if event.get("kind") == "board.create":
                try:
                    title = json.loads(event["body"])["title"]
                    if isinstance(title, str) and 0 < len(title) <= 100:
                        result.append({"id": eid, "title": title})
                except (ValueError, KeyError, TypeError):
                    continue
        return result[:100]

    def create_board(self, title, author):
        title = bounded(title, "title", 100)
        author = bounded(author, "author", 32)
        if len(self.boards()) >= 100:
            raise BoardError("Board limit reached")
        store = EventStore(self.path)
        try:
            return store.append("board.create", author, json.dumps({"title": title}))
        finally:
            store.close()

    def messages(self, board_id, page=1):
        if not isinstance(page, int) or not 1 <= page <= 10000:
            raise BoardError("Page out of range")
        if board_id not in {b["id"] for b in self.boards()}:
            raise BoardError("Unknown board")
        messages = []
        for eid, event in self.events():
            if event.get("kind") != "board.message":
                continue
            try:
                data = json.loads(event["body"])
                if data.get("board_id") == board_id:
                    messages.append({"id": eid, "author": event.get("author", "?"),
                                     "title": data["title"], "body": data["body"],
                                     "parent": data.get("parent")})
            except (ValueError, KeyError, TypeError):
                continue
        start = (page - 1) * 10
        return messages[start:start + 10]

    def post(self, board_id, author, title, body, parent=None):
        author = bounded(author, "author", 32)
        title = bounded(title, "title", 100)
        body = bounded(body, "body", 4000)
        if board_id not in {b["id"] for b in self.boards()}:
            raise BoardError("Unknown board")
        if parent is not None:
            target = next(((eid, event) for eid, event in self.events()
                           if eid == parent and event.get("kind") == "board.message"), None)
            if target is None:
                raise BoardError("Reply target missing")
            try:
                if json.loads(target[1]["body"]).get("board_id") != board_id:
                    raise BoardError("Reply target belongs to another board")
            except (ValueError, TypeError) as exc:
                raise BoardError("Invalid reply target") from exc
        payload = {"board_id": board_id, "title": title, "body": body, "parent": parent}
        store = EventStore(self.path)
        try:
            return store.append("board.message", author, json.dumps(payload, ensure_ascii=False),
                                parents=[parent] if parent else [])
        finally:
            store.close()
