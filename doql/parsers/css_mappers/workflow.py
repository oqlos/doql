"""Workflow and role CSS block mappers."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec, Interface, Page
    from ..css_utils import CssBlock, ParsedSelector


def _parse_step_text(step_text: str) -> "WorkflowStep":
    """Parse a 'action [target|params...]' step text into a WorkflowStep."""
    from ..models import WorkflowStep
    space_idx = step_text.find(' ')
    if space_idx == -1:
        return WorkflowStep(action=step_text, target=None, params={})
    action = step_text[:space_idx]
    rest = step_text[space_idx + 1:]
    target = None
    params: dict = {}
    if rest.startswith('cmd='):
        params['cmd'] = rest[4:].rstrip(';')
        target = 'cmd'
    else:
        for part in rest.split():
            if '=' in part:
                k, v = part.split('=', 1)
                params[k] = v.rstrip(';')
            elif target is None:
                target = part.rstrip(';')
    return WorkflowStep(action=action, target=target, params=params)


def _append_inline_steps(wf, block, strip_quotes_fn) -> None:
    """Append step-N inline declarations from *block* to *wf*."""
    for key, val in block.declarations.items():
        if key.startswith('step-'):
            wf.steps.append(_parse_step_text(strip_quotes_fn(val)))


def _append_child_steps(wf, block, parse_selector_fn, strip_quotes_fn) -> None:
    """Append steps from nested child blocks to *wf*."""
    from ..models import WorkflowStep
    for child in block.children:
        child_sel = parse_selector_fn(child.selector)
        if child_sel.type == 'step':
            wf.steps.append(WorkflowStep(
                action=strip_quotes_fn(child.declarations.get('action', '')),
                target=strip_quotes_fn(child.declarations.get('target', '')),
                params={k: strip_quotes_fn(v) for k, v in child.declarations.items()},
            ))


def _map_workflow(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Workflow definition."""
    from ..css_utils import _parse_selector, _strip_quotes
    from ..models import Workflow
    name = sel.attributes.get('name', '')
    existing = next((w for w in spec.workflows if w.name == name), None)
    if existing is None:
        wf = Workflow(
            name=name,
            trigger=_strip_quotes(block.declarations.get('trigger', '')),
        )
        spec.workflows.append(wf)
    else:
        wf = existing
        if not wf.trigger and block.declarations.get('trigger'):
            wf.trigger = _strip_quotes(block.declarations.get('trigger', ''))

    _append_inline_steps(wf, block, _strip_quotes)
    _append_child_steps(wf, block, _parse_selector, _strip_quotes)


def _map_role(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Role definition."""
    from ..css_utils import _parse_list
    from ..models import Role
    name = sel.attributes.get('name', '')
    can_str = block.declarations.get('can', '')
    permissions = _parse_list(can_str) if can_str else []
    role = Role(
        name=name,
        permissions=permissions,
    )
    spec.roles.append(role)
