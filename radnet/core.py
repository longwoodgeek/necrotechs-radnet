"""Append-only local event store. No cryptographic identity or federation yet."""
import hashlib
import json
import sqlite3
from pathlib import Path


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def event_id(event):
    return hashlib.sha256(canonical(event).encode("utf-8")).hexdigest()


class EventStore:
    def __init__(self, path):
        self.path = str(Path(path))
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            envelope TEXT NOT NULL,
            received_seq INTEGER NOT NULL UNIQUE
        )""")
        self.db.commit()

    def close(self):
        self.db.close()

    def append(self, kind, author, body, parents=None):
        if not kind or not author or not isinstance(body, str):
            raise ValueError("kind and author required; body must be text")
        parents = list(parents or [])
        if len(parents) != len(set(parents)) or any(not isinstance(p, str) or len(p) != 64 for p in parents):
            raise ValueError("parents must be unique SHA-256 identifiers")
        # Local sequence is an ordering of receipt, NOT proof of causal or wall-clock order.
        with self.db:
            seq = self.db.execute("SELECT COALESCE(MAX(received_seq), 0)+1 FROM events").fetchone()[0]
            envelope = {"schema": 1, "kind": kind, "author": author, "body": body, "parents": sorted(parents), "local_seq": seq}
            eid = event_id(envelope)
            self.db.execute("INSERT INTO events(id, envelope, received_seq) VALUES(?,?,?)", (eid, canonical(envelope), seq))
        return eid

    def get(self, eid):
        row = self.db.execute("SELECT envelope FROM events WHERE id=?", (eid,)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, limit=50):
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be 1..1000")
        return [{"id": eid, **json.loads(data)} for eid, data in self.db.execute(
            "SELECT id,envelope FROM events ORDER BY received_seq DESC LIMIT ?", (limit,))]

    def verify(self):
        bad = []
        for eid, data in self.db.execute("SELECT id,envelope FROM events"):
            try:
                if event_id(json.loads(data)) != eid:
                    bad.append(eid)
            except (ValueError, TypeError):
                bad.append(eid)
        return bad
