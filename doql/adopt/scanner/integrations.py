"""Integration scanning — external services from .env patterns."""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import DoqlSpec, Integration


_ENV_INTEGRATIONS: list[tuple[list[str], str, str]] = [
    (["SMTP", "EMAIL", "MAIL"], "email",   "smtp"),
    (["SLACK"],                  "slack",   "webhook"),
    (["STRIPE"],                 "stripe",  "payment"),
    (["S3", "MINIO", "STORAGE"], "storage", "s3"),
    (["MQTT"],                   "mqtt",    "mqtt"),
    (["MODBUS"],                 "modbus",  "hardware"),
    (["NLP"],                    "nlp",     "api"),
    (["GITHUB"],                 "github",  "scm"),
]


def scan_integrations(root: Path, spec: DoqlSpec) -> None:
    """Detect external integrations from .env and code."""
    env_text = " ".join(spec.env_refs).upper()
    for keywords, name, itype in _ENV_INTEGRATIONS:
        if any(kw in env_text for kw in keywords):
            spec.integrations.append(Integration(name=name, type=itype))
