"""Shared README generation for doql plugins."""
from __future__ import annotations


def generate_readme(
    plugin_name: str,
    modules: list[str],
    description: str,
    usage_extra: str = "",
) -> str:
    """Generate standard README.md content for a doql plugin.

    Args:
        plugin_name: Name of the plugin (e.g., "iso17025", "fleet")
        modules: List of generated module names
        description: Plugin description text
        usage_extra: Optional additional usage instructions

    Returns:
        README.md content as a string
    """
    modules_list = "\n".join(f"- `{m}`" for m in modules)

    usage_section = f"\n{usage_extra}\n" if usage_extra else ""

    return f"""# doql-plugin-{plugin_name}

{description}

## Generated modules

{modules_list}{usage_section}

## Usage

Add `PLUGINS: [doql-plugin-{plugin_name}]` to your `.doql` file.
"""
