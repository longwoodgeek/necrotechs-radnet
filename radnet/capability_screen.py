"""Read-only capability dashboard. Historical observations are not live probes."""
from pathlib import Path
import shutil
import textwrap
from .capabilities import read_evidence, describe_capability, CapabilityError

CAPABILITIES = (
    ("archive.local", "LOCAL ARCHIVE", "LOCAL SOFTWARE / NOT LIVE-VERIFIED"),
    ("boards.local", "MESSAGE BOARDS", "LOCAL SOFTWARE / NOT LIVE-VERIFIED"),
    ("captains_log.local", "CAPTAIN'S LOG", "LOCAL SOFTWARE / NOT LIVE-VERIFIED"),
    ("station.identity", "STATION IDENTITY", "SEE STATION STATUS"),
    ("reticulum.local", "RETICULUM", "NOT VERIFIED"),
    ("lora.transport", "LORA TRANSPORT", "NOT CONNECTED"),
    ("federation", "FEDERATION", "NOT IMPLEMENTED"),
)


def evidence_path(db_path):
    return Path(db_path).parent / "radnet-capability-evidence.jsonl"


def terminal_width(width=None):
    """Conservative terminal width, injectable for tests and small displays."""
    if width is None:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
    return max(24, min(int(width), 160))


def wrapped(lines, width):
    """Wrap without cutting meaningful status text or emitting wide lines."""
    result = []
    for line in lines:
        if not line:
            result.append("")
        else:
            result.extend(textwrap.wrap(line, width=width, break_long_words=True,
                                        break_on_hyphens=False, replace_whitespace=False))
    return "\n".join(result)


def dashboard(db_path, width=None):
    """Read-only status view; compact layout for narrow terminal windows."""
    width = terminal_width(width)
    path = evidence_path(db_path)
    lines = ["RADNET:// CAPABILITY REGISTRY",
             "LOCAL / UNVERIFIED",
             "NO LIVE HARDWARE PROBES", ""]
    try:
        records = read_evidence(path)
    except (CapabilityError, OSError, UnicodeError):
        return wrapped(lines + ["[ERROR] Capability evidence unreadable; no records trusted."], width)
    for key, label, baseline in CAPABILITIES:
        observed = describe_capability(records, key)
        count = observed["observations"]
        if width < 72:
            lines.extend([label, "  " + baseline])
            if count:
                lines.append(f"  HISTORICAL OBSERVATIONS: {count}")
            lines.append("")
        else:
            lines.append(f"{label:<20} {baseline}")
            if count:
                lines.append(f"  HISTORICAL OBSERVATIONS: {count}")
    lines += ["", f"EVIDENCE RECORDS: {len(records)}", "LIVE VERIFICATION: NONE",
              "[1] VIEW CAPABILITY EVIDENCE", "[0] RETURN"]
    return wrapped(lines, width)

def evidence_listing(db_path, width=None):
    """Show bounded recent historical records, sanitizing untrusted strings."""
    from .terminal import safe_text
    width = terminal_width(width)
    try:
        records = read_evidence(evidence_path(db_path))
    except (CapabilityError, OSError, UnicodeError):
        return "[ERROR] Capability evidence unreadable."
    lines = ["CAPABILITY EVIDENCE // LOCAL HISTORICAL OBSERVATIONS", "NOT PROOF OF CURRENT CONNECTIVITY"]
    for record in records[-10:]:
        lines.append(
            f"{safe_text(record.get('capability_id', '?'), 128)}: "
            f"{safe_text(record.get('result', '?'), 16)} "
            f"[{safe_text(record.get('method', '?'), 32)}] "
            f"{safe_text(record.get('receipt_time', '?'), 64)} "
            f"(clock unverified)"
        )
    if not records:
        lines.append("No evidence recorded.")
    return wrapped(lines, width)
