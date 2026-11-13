"""Truthful local-only startup diagnostics; no network or keys are probed."""
from pathlib import Path
import sqlite3

BANNER = """=========================================
       N E C R O T E C H S
             R A D N E T
========================================="""

def render_boot(db_path: str) -> str:
    path = Path(db_path)
    if path.exists():
        try:
            with sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True) as db:
                ok = db.execute("PRAGMA quick_check").fetchone()[0] == "ok"
                journal = "[ OK ] Existing SQLite journal readable" if ok else "[FAIL] SQLite integrity check failed"
        except (sqlite3.Error, OSError):
            journal = "[FAIL] Existing SQLite journal unavailable"
    else:
        journal = "[ -- ] No local journal yet (created on first post)"
    return "\n".join([
        BANNER,
        "RADNET SYSTEM INITIALIZATION",
        "[ OK ] Python runtime",
        journal,
        "[ -- ] Cryptographic identity not implemented",
        "[ -- ] Federation transport not implemented",
        "[ -- ] AXIS connector not installed",
        "",
        "NODE MODE       : LOCAL DEVELOPMENT",
        "SECURITY STATUS : EXPERIMENTAL / NOT SECURE",
        "MESSAGE NETWORK : NOT CONNECTED",
        "",
        "> WELCOME TO RADNET_",
        "> THE NETWORK REMEMBERS.",
    ])
