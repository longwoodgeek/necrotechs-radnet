"""Read-only Captain's Log projections for the loopback Doorbell."""
from .captains_log import CaptainsLog, LogError
from .terminal import safe_text


def entries(db_path, number=1):
    try:
        records = CaptainsLog(db_path).browse(number)
    except LogError:
        return "CAPTAIN'S LOG\nJournal unavailable or invalid.", []
    lines = ["CAPTAIN'S LOG // LOCAL ARCHIVE",
             "AUTHORS / CLOCKS UNVERIFIED",
             "LATEST REVISION PER ENTRY",
             f"PAGE {number}", ""]
    for index, record in enumerate(records, 1):
        lines.append(f"[{index}] {safe_text(record['data']['title'], 100)}")
        lines.append(f"  Receipt order: {record['received_seq']}")
    if not records:
        lines.append("No entries on this page.")
    return "\n".join(lines), records


def detail(record):
    data = record["data"]
    receipt = data["receipt"]
    fields = [
        "CAPTAIN'S LOG // ENTRY",
        "CORRECTION" if record["envelope"]["kind"] == "log.correct" else "ORIGINAL",
        "Title: " + safe_text(data["title"], 100),
        "Operator: " + safe_text(record["envelope"]["author"], 32) + " [UNVERIFIED]",
        "Entry ID: " + safe_text(record["entry_id"], 64),
        "Event ID: " + safe_text(record["id"], 64),
        f"Receipt order: {record['received_seq']} (local only)",
        "Claimed time: " + safe_text(data["claimed_time"] or "not supplied", 64),
        "Claimed source: " + safe_text(data["time_source"], 200),
        "Claimed uncertainty: " + safe_text(data["uncertainty"], 200),
        "Receipt time: " + safe_text(receipt["time"], 64),
        "Receipt source: " + safe_text(receipt["source"], 64),
        "Receipt uncertainty: " + safe_text(receipt["uncertainty"], 200),
        "Provenance: " + safe_text(data["provenance"], 100),
        "Correction reason: " + safe_text(data.get("reason") or "none", 500),
        "HASHES ARE NOT SIGNATURES",
        "",
        safe_text(data["body"], 4000),
    ]
    return "\n".join(fields)


def revisions(db_path, entry_id, number=1):
    try:
        records = CaptainsLog(db_path).history(entry_id, number)
    except LogError:
        return "REVISION HISTORY\nJournal unavailable or invalid.", []
    lines = ["CAPTAIN'S LOG // REVISION HISTORY", "ORIGINALS RETAINED", f"PAGE {number}", ""]
    for index, record in enumerate(records, 1):
        kind = "CORRECTION" if record["envelope"]["kind"] == "log.correct" else "ORIGINAL"
        lines.append(f"[{index}] {kind} // receipt {record['received_seq']}")
    return "\n".join(lines), records
