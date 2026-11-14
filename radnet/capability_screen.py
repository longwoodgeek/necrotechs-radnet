"""Read-only capability dashboard. Historical observations are not live probes."""
from pathlib import Path
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


def dashboard(db_path):
    """Render only supported claims, never probe or create files."""
    path = evidence_path(db_path)
    lines = ["RADNET:// CAPABILITY REGISTRY", "LOCAL / UNVERIFIED // NO LIVE HARDWARE PROBES", ""]
    try:
        records = read_evidence(path)
    except (CapabilityError, OSError, UnicodeError):
        return "\n".join(lines + ["[ERROR] Capability evidence unreadable; no records trusted."])
    for key, label, baseline in CAPABILITIES:
        observed = describe_capability(records, key)
        suffix = f" // {observed['observations']} historical observation(s)" if observed["observations"] else ""
        lines.append(f"{label:<20} {baseline}{suffix}")
    lines += ["", f"EVIDENCE RECORDS: {len(records)}", "LIVE VERIFICATION: NONE", "[1] VIEW CAPABILITY EVIDENCE  [0] RETURN"]
    return "\n".join(lines)


def evidence_listing(db_path):
    """Show bounded recent historical records, sanitizing untrusted strings."""
    from .terminal import safe_text
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
    return "\n".join(lines)
