"""Environment scanning — .env files and docker-compose variants."""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import DoqlSpec, Environment
from .utils import find_compose, load_yaml


def scan_environments(root: Path, spec: DoqlSpec) -> None:
    """Detect environments from .env files and docker-compose variants."""
    # Local environment (always present)
    local_env = Environment(name="local")
    if (root / ".env").exists():
        local_env.env_file = ".env"
    local_env.runtime = spec.deploy.target if spec.deploy else "docker-compose"
    spec.environments.append(local_env)

    # Detect staging/prod from .env.* files
    for env_file in sorted(root.glob(".env.*")):
        name = env_file.name.split(".", 2)[-1]  # .env.staging → staging
        if name in ("example", "local", "docker", "test", "bak"):
            continue
        env = Environment(name=name, env_file=env_file.name)
        env.runtime = spec.deploy.target if spec.deploy else "docker-compose"

        # Check for ssh_host in env vars
        for ref in spec.env_refs:
            if name.upper() in ref.upper() and "HOST" in ref.upper():
                env.ssh_host = f"env.{ref}"
                break
        spec.environments.append(env)

    # Detect from docker-compose variant files
    compose_patterns = [
        ("dev", ["docker-compose.dev.yml", "docker/docker-compose.dev.yml",
                  "infra/docker/dev/docker-compose.dev.yml"]),
        ("staging", ["docker-compose.staging.yml", "docker/docker-compose.staging.yml"]),
        ("prod", ["docker-compose.prod.yml", "docker/docker-compose.prod.yml",
                   "infra/docker/prod/docker-compose.prod.yml"]),
    ]
    for env_name, paths in compose_patterns:
        if any(e.name == env_name for e in spec.environments):
            continue
        for p in paths:
            if (root / p).exists():
                env = Environment(name=env_name, runtime="docker-compose")
                env_file = root / f".env.{env_name}"
                if env_file.exists():
                    env.env_file = env_file.name
                spec.environments.append(env)
                break
