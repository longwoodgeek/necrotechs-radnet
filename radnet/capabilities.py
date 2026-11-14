"""Append-only local capability evidence, without live hardware claims.

JSONL is intentionally independent of station identity and the SQLite journal.
Evidence is local and unverified; callers must not present it as authentication.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

VALID_RESULTS = frozenset({"pass", "fail", "unknown"})
VALID_METHODS = frozenset({"manual", "automated", "simulation"})


class CapabilityError(ValueError):
    pass


def append_evidence(path, capability_id, result, method, source, *, detail=""):
    """Append one observation; return the receipt record. Never rewrite history."""
    if not isinstance(capability_id, str) or not capability_id or len(capability_id) > 128 or not all(c.isascii() and (c.isalnum() or c in "._-") for c in capability_id):
        raise CapabilityError("invalid capability identifier")
    if result not in VALID_RESULTS or method not in VALID_METHODS:
        raise CapabilityError("invalid evidence result or method")
    if not isinstance(source, str) or not source.strip() or len(source) > 256:
        raise CapabilityError("invalid evidence source")
    if not isinstance(detail, str) or len(detail) > 4096:
        raise CapabilityError("invalid evidence detail")
    record = {
        "schema": 1,
        "capability_id": capability_id,
        "result": result,
        "method": method,
        "source": source,
        "detail": detail,
        "receipt_time": datetime.now(timezone.utc).isoformat(),
        "receipt_clock": "local_system_clock_unverified",
    }
    destination = Path(path)
    # Never overwrite existing history. Exclusive append protects each write.
    data = (json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    fd = os.open(destination, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    return record


def read_evidence(path):
    """Read all observations in file order, refusing malformed lines."""
    destination = Path(path)
    if not destination.exists():
        return []
    records = []
    with destination.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, 1):
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CapabilityError(f"malformed evidence at line {index}") from exc
            if not isinstance(item, dict) or item.get("schema") != 1:
                raise CapabilityError(f"invalid evidence schema at line {index}")
            records.append(item)
    return records


def describe_capability(records, capability_id):
    """Describe historical observations; never infer current operational state."""
    matches = [r for r in records if r.get("capability_id") == capability_id]
    return {
        "capability_id": capability_id,
        "observations": len(matches),
        "last_result": matches[-1]["result"] if matches else None,
        "operational_now": "NOT VERIFIED",
    }
