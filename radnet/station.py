"""Local, explicit station identity. Never interprets configuration as proof of connectivity."""
import json
import os
from pathlib import Path
import uuid

SCHEMA = 1

class StationError(ValueError):
    pass

def _validate(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise StationError("unsupported station identity schema")
    try:
        station_id = str(uuid.UUID(data["station_id"]))
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise StationError("invalid station ID") from exc
    if station_id != data["station_id"]:
        raise StationError("station ID must be canonical")
    label = data.get("label")
    if not isinstance(label, str) or not 1 <= len(label) <= 64 or any(ord(c) < 32 or ord(c) == 127 for c in label):
        raise StationError("invalid station label")
    if set(data) != {"schema", "station_id", "label"}:
        raise StationError("unexpected station identity fields")
    return data

def load(path):
    """Read only. Missing identity is reported as absent, never silently generated."""
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as stream:
            return _validate(json.load(stream))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StationError("station identity unreadable") from exc

def initialize(path, label):
    """Explicitly create a portable station identity; refuse overwrite and symlink targets."""
    path = Path(path)
    record = _validate({"schema": SCHEMA, "station_id": str(uuid.uuid4()), "label": label})
    # Exclusive creation prevents replacing an existing station identity.
    payload = (json.dumps(record, sort_keys=True, indent=2) + "\n").encode("utf-8")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    return record

def status(path):
    """Configured identity is not authenticated identity or transport verification."""
    try:
        identity = load(path)
    except StationError:
        return "Station identity: INVALID / UNREADABLE\nIdentity verification: NOT IMPLEMENTED"
    if identity is None:
        return "Station identity: NOT CONFIGURED\nIdentity verification: NOT IMPLEMENTED"
    return (f"Station label: {identity['label']} [LOCAL CONFIGURATION ONLY]\n"
            f"Station ID: {identity['station_id']}\n"
            "Identity verification: NOT IMPLEMENTED\n"
            "Transport connectivity: NOT VERIFIED")
