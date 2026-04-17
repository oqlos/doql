"""CSS ↔ LESS / SASS format conversion."""
from __future__ import annotations


def _css_to_less(css_text: str) -> str:
    """Wrap CSS output with a LESS variable header comment."""
    header = "// LESS format — define @variables here as needed\n\n"
    return header + css_text


def _css_to_sass(css_text: str) -> str:
    """Convert CSS syntax to SASS (indented, no braces/semicolons)."""
    lines = []
    for line in css_text.splitlines():
        stripped = line.rstrip()
        # Skip empty lines
        if not stripped:
            lines.append("")
            continue
        # Comments pass through
        if stripped.startswith("//") or stripped.startswith("/*"):
            lines.append(stripped)
            continue
        if stripped.endswith("*/"):
            lines.append(stripped)
            continue
        # Opening brace — just remove it
        if stripped.endswith("{"):
            lines.append(stripped[:-1].rstrip())
            continue
        # Closing brace — skip
        if stripped.strip() == "}":
            continue
        # Property — remove trailing semicolon
        if stripped.rstrip().endswith(";"):
            lines.append(stripped.rstrip()[:-1])
            continue
        lines.append(stripped)
    return "\n".join(lines) + "\n"
