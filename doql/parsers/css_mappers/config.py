"""Template, document, and report CSS block mappers."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..models import DoqlSpec
    from ..css_utils import CssBlock, ParsedSelector


def _map_config_block(
    spec: "DoqlSpec",
    sel: "ParsedSelector", 
    block: "CssBlock",
    model_class: type,
    list_attr: str,
    defaults: dict[str, str],
    list_fields: dict[str, str],
) -> None:
    """Generic config block mapper for Template/Document/Report.
    
    Args:
        spec: DoqlSpec to append to
        sel: Parsed CSS selector
        block: CSS block with declarations
        model_class: Model class to instantiate (Template, Document, Report)
        list_attr: Attribute name on spec to append to (templates, documents, reports)
        defaults: Default values for model fields
        list_fields: Field names that should be parsed as lists (field_name -> parse_key)
    """
    name = sel.attributes.get('name', '')
    kwargs: dict[str, Any] = {'name': name}
    
    for field, default in defaults.items():
        kwargs[field] = block.declarations.get(field, default)
    
    for field, parse_key in list_fields.items():
        list_str = block.declarations.get(parse_key)
        if list_str:
            from ..css_utils import _parse_list
            kwargs[field] = _parse_list(list_str)
    
    obj = model_class(**kwargs)
    getattr(spec, list_attr).append(obj)


def _map_template(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Template definition."""
    from ..models import Template
    _map_config_block(
        spec, sel, block,
        model_class=Template,
        list_attr='templates',
        defaults={'type': 'html', 'file': ''},
        list_fields={'vars': 'vars'},
    )


def _map_document(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Document definition."""
    from ..models import Document
    _map_config_block(
        spec, sel, block,
        model_class=Document,
        list_attr='documents',
        defaults={'type': 'pdf', 'template': ''},
        list_fields={'partials': 'partials'},
    )


def _map_report(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Report definition."""
    from ..models import Report
    name = sel.attributes.get('name', '')
    report = Report(
        name=name,
        schedule=block.declarations.get('schedule', ''),
        template=block.declarations.get('template', ''),
        output=block.declarations.get('output', 'pdf'),
    )
    spec.reports.append(report)
