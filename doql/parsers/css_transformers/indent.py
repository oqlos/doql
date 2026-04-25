"""Convert indent-based SASS blocks to brace-delimited CSS."""
from __future__ import annotations

from .selectors import _is_step_line, _is_selector_starter, _find_step_block_end


def _close_indent_blocks(
    result_lines: list[str], indent_stack: list[int], current_indent: int
) -> None:
    """Emit closing braces for all blocks whose indent exceeds *current_indent*."""
    while indent_stack and current_indent <= indent_stack[-1]:
        indent_stack.pop()
        result_lines.append('  ' * len(indent_stack) + '}')


def _convert_indent_to_braces(lines: list[str]) -> list[str]:
    """Convert indent-based SASS blocks to brace-delimited CSS."""
    result_lines: list[str] = []
    indent_stack: list[int] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        if not stripped:
            i += 1
            continue

        current_indent = len(line) - len(line.lstrip())
        _close_indent_blocks(result_lines, indent_stack, current_indent)

        if _is_step_line(line):
            block_end = _find_step_block_end(lines, i, current_indent)
            step_lines = [stripped.lstrip()] + [lines[j] for j in range(i + 1, block_end)]
            step_value = '\n'.join(step_lines).rstrip()
            if not step_value.endswith(';'):
                step_value += ';'
            result_lines.append('  ' * len(indent_stack) + step_value)
            i = block_end
            continue

        if _is_selector_starter(line):
            result_lines.append('  ' * len(indent_stack) + stripped.lstrip() + ' {')
            indent_stack.append(current_indent)
        else:
            prop_line = stripped.lstrip()
            if not prop_line.endswith(';'):
                prop_line += ';'
            result_lines.append('  ' * len(indent_stack) + prop_line)

        i += 1

    while indent_stack:
        indent_stack.pop()
        result_lines.append('  ' * len(indent_stack) + '}')

    return result_lines
