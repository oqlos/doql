import re
from pathlib import Path

def clean_value(val: str) -> str:
    return val.strip().strip("'").strip('"')

def convert_dsl_to_doql(dsl_text: str, default_name: str = "oql_workflow") -> str:
    lines = dsl_text.splitlines()
    workflow_name = default_name
    steps = []

    # Simple regexes to match OQL commands
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

        # Check for SET NAME
        match = set_name_re.match(line)
        if match:
            # Slugify the workflow name
            raw_name = clean_value(match.group(1))
            workflow_name = re.sub(r"[^a-zA-Z0-9_\-:]", "_", raw_name.lower())
            continue

        # Check for LOG
        match = log_re.match(line)
        if match:
            val = clean_value(match.group(1))
            steps.append(f"run cmd=echo \"{val}\"")
            continue

        # Check for SET var val
        match = set_var_re.match(line)
        if match:
            var = match.group(1)
            val = clean_value(match.group(2))
            steps.append(f"run cmd=\"{var} SET {val}\"")
            continue

        # Check for IF
        match = if_re.match(line)
        if match:
            val = clean_value(match.group(1))
            steps.append(f"assert cond=\"{val}\"")
            continue

        # Check for ASSERT
        match = assert_re.match(line)
        if match:
            val = clean_value(match.group(1))
            steps.append(f"assert cond=\"{val}\"")
            continue

        # Check for ERROR / CORRECT
        match = error_re.match(line)
        if match:
            val = clean_value(match.group(1))
            steps.append(f"run cmd=\"echo ERROR: {val}\"")
            continue

        match = correct_re.match(line)
        if match:
            val = clean_value(match.group(1))
            steps.append(f"run cmd=\"echo CORRECT: {val}\"")
            continue

        # Fallback step
        steps.append(f"run cmd=\"{line}\"")

    # Format the DOQL workflow output
    out = []
    out.append(f'workflow[name="{workflow_name}"] {{')
    out.append('  trigger: manual;')
    for idx, step in enumerate(steps, 1):
        out.append(f'  step-{idx}: {step};')
    out.append('}')

    return "\n".join(out) + "\n"
