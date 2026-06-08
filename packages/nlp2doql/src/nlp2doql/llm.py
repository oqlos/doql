"""Optional litellm planner for NL → DOQL."""

from __future__ import annotations

import json
import re

from nlp2doql.models import BlockPlan, DoqlPlan
from nlp2doql.rules import plan_with_rules


def _parse_llm_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("LLM response did not contain JSON")
    return json.loads(match.group(0))


def plan_with_litellm(prompt: str, *, model: str) -> DoqlPlan:
    try:
        import litellm
    except ImportError as exc:
        raise RuntimeError("litellm not installed; pip install 'nlp2doql[llm]'") from exc

    system = (
        "You generate DOQL blocks in CSS-like LESS syntax. "
        "Return JSON: {\"title\": str, \"blocks\": [{\"selector\": str, \"properties\": {k:v}}]}. "
        "Use selectors like app, entity[name=\"X\"], interface[type=\"web\"], workflow[name=\"test\"]."
    )
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content or ""
    payload = _parse_llm_json(content)
    blocks = [
        BlockPlan(
            selector=item["selector"],
            properties={str(k): str(v) for k, v in (item.get("properties") or {}).items()},
        )
        for item in payload.get("blocks") or []
    ]
    if not blocks:
        return plan_with_rules(prompt)
    return DoqlPlan(
        title=str(payload.get("title") or prompt[:80]),
        blocks=blocks,
        planner="litellm",
        confidence=0.8,
        rationale=f"litellm model={model}",
    )
