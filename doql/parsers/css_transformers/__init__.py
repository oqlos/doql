"""CSS format transformers.

Converts between CSS-like formats:
  - SASS → CSS (indent-based to brace-delimited)
  - LESS variable resolution
  - SASS variable resolution
"""
from __future__ import annotations

from .variables import _resolve_vars, _resolve_less_vars, _resolve_sass_vars
from .mixins import _extract_mixins, _expand_includes
from .indent import _convert_indent_to_braces


def _sass_to_css(text: str) -> str:
    """Convert indent-based SASS to brace-delimited CSS for unified parsing.

    This is a minimal conversion — enough for DOQL semantics.
    Strips @mixin definitions and expands @include as comments.
    """
    text = _resolve_sass_vars(text)

    # Collect mixins and expand includes
    lines = text.splitlines()
    mixins, remaining = _extract_mixins(lines)
    expanded = _expand_includes(remaining, mixins)

    # Convert indent-based blocks to CSS braces
    result_lines = _convert_indent_to_braces(expanded)
    return '\n'.join(result_lines)
