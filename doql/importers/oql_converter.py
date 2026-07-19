"""Convert OQL/CQL scenario DSL files to DOQL workflow blocks."""

from __future__ import annotations

__all__ = ["clean_value", "convert_dsl_to_doql"]

try:
    from dsl2doql.converter import clean_value, convert_dsl_to_doql  # type: ignore[import-untyped]
except ImportError:
    # Fallback to local implementation if package not installed
    import re

    def clean_value(val: str) -> str:
        return val.strip().strip("'").strip('"')

    def convert_dsl_to_doql(dsl_text: str, default_name: str = "oql_workflow") -> str:
        """Map OQL scenario commands to a DOQL ``workflow[name="..."]`` block."""
        lines = dsl_text.splitlines()
        workflow_name = default_name
        steps: list[str] = []

        set_name_re = re.compile(r"SET\s+NAME\s+(.+)", re.IGNORECASE)
        set_var_re = re.compile(r"SET\s+(\w+)\s+(.+)", re.IGNORECASE)
        log_re = re.compile(r"LOG\s+(.+)", re.IGNORECASE)
        if_re = re.compile(r"IF\s+(.+)", re.IGNORECASE)
        assert_re = re.compile(r"ASSERT\s+(.+)", re.IGNORECASE)
        error_re = re.compile(r"ERROR\s+(.+)", re.IGNORECASE)
        correct_re = re.compile(r"CORRECT\s+(.+)", re.IGNORECASE)

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("VERSION:") or line.startswith("GOAL:"):
                continue

            match = set_name_re.match(line)
            if match:
                raw_name = clean_value(match.group(1))
                workflow_name = re.sub(r"[^a-zA-Z0-9_\-:]", "_", raw_name.lower())
                continue

            match = log_re.match(line)
            if match:
                val = clean_value(match.group(1))
                steps.append(f'run cmd=echo "{val}"')
                continue

            match = set_var_re.match(line)
            if match:
                var = match.group(1)
                val = clean_value(match.group(2))
                steps.append(f'run cmd="{var} SET {val}"')
                continue

            match = if_re.match(line)
            if match:
                val = clean_value(match.group(1))
                steps.append(f'assert cond="{val}"')
                continue

            match = assert_re.match(line)
            if match:
                val = clean_value(match.group(1))
                steps.append(f'assert cond="{val}"')
                continue

            match = error_re.match(line)
            if match:
                val = clean_value(match.group(1))
                steps.append(f'run cmd="echo ERROR: {val}"')
                continue

            match = correct_re.match(line)
            if match:
                val = clean_value(match.group(1))
                steps.append(f'run cmd="echo CORRECT: {val}"')
                continue

            steps.append(f'run cmd="{line}"')

        out = [f'workflow[name="{workflow_name}"] {{', "  trigger: manual;"]
        for idx, step in enumerate(steps, 1):
            out.append(f"  step-{idx}: {step};")
        out.append("}")
        return "\n".join(out) + "\n"
