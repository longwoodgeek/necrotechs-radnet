"""ANSI severity rendering for RadNet terminals.

Color is supplementary: explicit severity words remain in plain output.
"""
import re

RESET = "\x1b[0m"
COLORS = {
    "OK": "\x1b[32m",
    "INFO": "\x1b[37m",
    "WARN": "\x1b[33m",
    "ERROR": "\x1b[31m",
    "CRITICAL": "\x1b[1;31m",
}
_CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def severity(level, message, *, ansi=False):
    """Render a labeled severity message, escaping untrusted controls."""
    level = str(level).upper()
    if level not in COLORS:
        raise ValueError("unknown severity")
    clean = _CONTROL.sub(" ", str(message))
    text = f"[{level}] {clean}"
    return f"{COLORS[level]}{text}{RESET}" if ansi else text


def colorize_status(text, *, ansi=False):
    """Color known status labels without inventing error conditions."""
    lines = []
    for line in text.split("\n"):
        if line.startswith("Station identity: INVALID") or line.startswith("IDENTIFICATION: INVALID"):
            lines.append(severity("ERROR", line, ansi=ansi))
        elif line.startswith("Journal unavailable"):
            lines.append(severity("ERROR", line, ansi=ansi))
        elif line.startswith("DRINKING PRIVILEGES:"):
            lines.append(line)  # humor is not a critical incident
        else:
            lines.append(line)
    return "\n".join(lines)
