"""Integration scanning — external services from .env patterns."""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import DoqlSpec, Integration


def scan_integrations(root: Path, spec: DoqlSpec) -> None:
    """Detect external integrations from .env and code."""
    env_text = " ".join(spec.env_refs).upper()

    if "SMTP" in env_text or "EMAIL" in env_text or "MAIL" in env_text:
        spec.integrations.append(Integration(name="email", type="smtp"))

    if "SLACK" in env_text:
        spec.integrations.append(Integration(name="slack", type="webhook"))

    if "STRIPE" in env_text:
        spec.integrations.append(Integration(name="stripe", type="payment"))

    if "S3" in env_text or "MINIO" in env_text or "STORAGE" in env_text:
        spec.integrations.append(Integration(name="storage", type="s3"))

    if "MQTT" in env_text:
        spec.integrations.append(Integration(name="mqtt", type="mqtt"))

    if "MODBUS" in env_text:
        spec.integrations.append(Integration(name="modbus", type="hardware"))

    if "NLP" in env_text:
        spec.integrations.append(Integration(name="nlp", type="api"))

    if "GITHUB" in env_text:
        spec.integrations.append(Integration(name="github", type="scm"))
