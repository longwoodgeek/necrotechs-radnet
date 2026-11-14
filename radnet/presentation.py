"""Shared plain-text rendering rules for RadNet terminal clients."""
import textwrap

DEFAULT_REMOTE_WIDTH = 36
MIN_WIDTH = 24
MAX_WIDTH = 160


def normalized_width(width=None):
    """Unknown remote client width uses a conservative compact layout."""
    if width is None:
        width = DEFAULT_REMOTE_WIDTH
    return max(MIN_WIDTH, min(int(width), MAX_WIDTH))


def wrap_lines(lines, width=None):
    """Wrap each logical line without losing blank lines."""
    width = normalized_width(width)
    rendered = []
    for line in lines:
        if not line:
            rendered.append("")
        else:
            rendered.extend(textwrap.wrap(
                str(line), width=width, break_long_words=True,
                break_on_hyphens=False, replace_whitespace=False,
            ))
    return "\n".join(rendered)


def safe_multiline(message, limit=8192):
    """Preserve intentional newlines while stripping untrusted controls."""
    from .terminal import safe_text
    return "\n".join(safe_text(line, limit) for line in str(message).splitlines())[:limit]


def render_remote(message, width=None):
    return wrap_lines(safe_multiline(message).split("\n"), width) + "\n"
