"""Export TypeScript SDK from DoqlSpec."""
from __future__ import annotations

from typing import IO

from ..parser import DoqlSpec


def run(spec: DoqlSpec, out: IO[str]) -> None:
    """Write TypeScript SDK to the given stream."""
    out.write("// Auto-generated TypeScript SDK\n")
    out.write(f"// Application: {spec.app_name}\n\n")
    out.write("const BASE_URL = process.env.API_URL || 'http://localhost:8000';\n\n")
    for e in spec.entities:
        name = e.name
        lower = name.lower()
        out.write(f"export async function list{name}s() {{\n")
        out.write(f"  return fetch(`${{BASE_URL}}/api/v1/{lower}s`).then(r => r.json());\n")
        out.write("}\n\n")
        out.write(f"export async function create{name}(data: Record<string, unknown>) {{\n")
        out.write(f"  return fetch(`${{BASE_URL}}/api/v1/{lower}s`, {{\n")
        out.write("    method: 'POST',\n")
        out.write("    headers: { 'Content-Type': 'application/json' },\n")
        out.write("    body: JSON.stringify(data),\n")
        out.write("  }).then(r => r.json());\n")
        out.write("}\n\n")
