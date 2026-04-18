"""CSS ↔ LESS / SASS format conversion."""
from __future__ import annotations


def _css_to_less(css_text: str) -> str:
    """Convert CSS output to LESS format.
    
    LESS uses @variables and doesn't require quotes for simple string values.
    """
    import re
    
    header = "// LESS format — define @variables here as needed\n\n"
    
    lines = []
    for line in css_text.splitlines():
        # Skip empty lines at start (we'll add our own header)
        if not lines and not line.strip():
            continue
            
        # Convert property lines - remove quotes from simple string values
        # Match: property: "simple-value"; -> property: simple-value;
        # But keep quotes for: values with spaces, special chars, or env.
        def unquote_simple_values(match):
            full_prop = match.group(1)  # includes indentation
            val = match.group(2)
            
            # Keep quotes for complex values
            if ' ' in val or ',' in val or '(' in val or ')' in val:
                return f'{full_prop}: "{val}";'
            if val.startswith('env.') or val.startswith('$') or val.startswith('@'):
                return f'{full_prop}: {val};'
            if val in ('true', 'false', 'null'):
                return f'{full_prop}: {val};'
            if val.replace('.', '', 1).replace('-', '', 1).isdigit():
                return f'{full_prop}: {val};'
            
            # Simple value - remove quotes
            return f'{full_prop}: {val};'
        
        # Pattern: property: "value"; (with optional indentation)
        line = re.sub(r'^(\s*[\w\-@]+):\s*"([^"]+)"\s*;?$', unquote_simple_values, line)
        lines.append(line)
    
    return header + '\n'.join(lines) + '\n'


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
