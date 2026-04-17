"""Extraction utilities for parsing .doql block bodies."""
from __future__ import annotations

import re
from typing import Optional

from .models import EntityField, Page


def extract_val(body: str, key: str) -> Optional[str]:
    """Extract 'key: value' from an indented block body."""
    m = re.search(rf'^\s+{re.escape(key)}:[ \t]*(.+)', body, re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).strip()
    # Handle quoted strings — extract content inside first pair of quotes
    qm = re.match(r'^"([^"]*)"', raw) or re.match(r"^'([^']*)'", raw)
    if qm:
        return qm.group(1)
    # Strip inline comment for unquoted values
    if "  #" in raw:
        raw = raw[:raw.index("  #")]
    elif "\t#" in raw:
        raw = raw[:raw.index("\t#")]
    return raw.strip()


def extract_list(body: str, key: str) -> list[str]:
    """Extract 'key: [a, b, c]' or 'key: value' from body."""
    raw = extract_val(body, key)
    if not raw:
        return []
    raw = raw.strip("[]")
    return [v.strip().strip('"').strip("'") for v in raw.split(",") if v.strip()]


def extract_yaml_list(body: str, key: str) -> list[str]:
    """Extract YAML-style list items under a key: header."""
    m = re.search(rf'^\s+{re.escape(key)}:[ \t]*$', body, re.MULTILINE)
    if not m:
        return []
    start = m.end()
    items: list[str] = []
    for line in body[start:].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        else:
            break
    return items


def _extract_page_from_format1(body: str) -> list[Page]:
    """Extract pages using PAGE keyword format."""
    pages: list[Page] = []
    for m in re.finditer(r'^\s+PAGE\s+(\w+):', body, re.MULTILINE):
        name = m.group(1)
        page_start = m.end()
        next_page = re.search(r'^\s+PAGE\s+\w+:', body[page_start:], re.MULTILINE)
        next_top = re.search(r'^[A-Z]', body[page_start:], re.MULTILINE)
        end = len(body)
        if next_page:
            end = min(end, page_start + next_page.start())
        if next_top:
            end = min(end, page_start + next_top.start())
        sub = body[page_start:end]
        layout = extract_val(sub, "layout")
        path = extract_val(sub, "path")
        public_s = extract_val(sub, "public")
        pages.append(Page(
            name=name,
            layout=layout,
            path=path,
            public=public_s == "true" if public_s else False,
        ))
    return pages


def _extract_page_from_format2(body: str) -> list[Page]:
    """Extract pages using PAGES: YAML list format."""
    pages: list[Page] = []
    pages_m = re.search(r'^(\s+)PAGES:[ \t]*$', body, re.MULTILINE)
    if not pages_m:
        return pages

    pages_indent = len(pages_m.group(1))
    pages_body = body[pages_m.end():]
    first_item = re.search(r'^(\s+)-\s+(\w+):', pages_body, re.MULTILINE)
    if not first_item:
        return pages

    item_indent = first_item.group(1)
    item_re = re.compile(rf'^{re.escape(item_indent)}-\s+(\w+):', re.MULTILINE)
    matches = list(item_re.finditer(pages_body))
    for idx, item_m in enumerate(matches):
        name = item_m.group(1)
        item_start = item_m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(pages_body)
        sub = pages_body[item_start:end]
        layout = extract_val(sub, "layout")
        path = extract_val(sub, "path")
        public_s = extract_val(sub, "public")
        pages.append(Page(
            name=name,
            layout=layout,
            path=path,
            public=public_s == "true" if public_s else False,
        ))
    return pages


def extract_pages(body: str) -> list[Page]:
    """Extract PAGE definitions from INTERFACE body.

    Supports two formats:
      1. ``PAGE name:``  (web/mobile/desktop)
      2. ``PAGES:`` followed by ``- name:``  (kiosk)
    """
    # Try format 1 first (PAGE keyword)
    pages = _extract_page_from_format1(body)
    
    # Fall back to format 2 (PAGES: YAML list)
    if not pages:
        pages = _extract_page_from_format2(body)

    return pages


def _should_skip_line(line: str) -> bool:
    """Check if a line should be skipped during field extraction."""
    if not line:
        return True
    skip_prefixes = ("#", "COMPUTED", "INDEX", "AUDIT", "IF ", "ELSE")
    if line.startswith(skip_prefixes):
        return True
    if ":" not in line:
        return True
    return False


def _is_valid_field_name(name: str) -> bool:
    """Check if field name is valid (starts with lowercase)."""
    return bool(name and name[0].islower())


def _parse_field_flags(ftype_raw: str) -> dict[str, bool]:
    """Parse field flags from type string."""
    return {
        "required": "!" in ftype_raw,
        "unique": "unique" in ftype_raw.lower(),
        "auto": "auto" in ftype_raw.lower(),
        "computed": "computed" in ftype_raw.lower(),
    }


def _parse_field_ref(ftype_raw: str) -> str | None:
    """Extract reference entity from type string."""
    ref_m = re.search(r'(\w+)\s+ref', ftype_raw)
    return ref_m.group(1) if ref_m else None


def _parse_field_default(ftype_raw: str) -> str | None:
    """Extract default value from type string."""
    default_m = re.search(r'default=(\S+)', ftype_raw)
    return default_m.group(1) if default_m else None


def _parse_field_type(ftype_raw: str) -> str:
    """Extract clean base type from type string."""
    return re.split(r'[!\s]', ftype_raw)[0]


def extract_entity_fields(body: str) -> list[EntityField]:
    """Extract field definitions from ENTITY body."""
    fields: list[EntityField] = []
    for line in body.splitlines():
        line = line.strip()
        if _should_skip_line(line):
            continue

        parts = line.split(":", 1)
        fname = parts[0].strip()
        ftype_raw = parts[1].strip() if len(parts) > 1 else "string"

        if not _is_valid_field_name(fname):
            continue

        flags = _parse_field_flags(ftype_raw)
        ref = _parse_field_ref(ftype_raw)
        default = _parse_field_default(ftype_raw)
        base_type = _parse_field_type(ftype_raw)

        fields.append(EntityField(
            name=fname, type=base_type, required=flags["required"],
            unique=flags["unique"], computed=flags["computed"], ref=ref,
            default=default, auto=flags["auto"],
        ))
    return fields


def collect_env_refs(text: str) -> list[str]:
    """Find all env.VAR_NAME references in the text."""
    return sorted(set(re.findall(r'env\.([A-Z_][A-Z0-9_]*)', text)))
