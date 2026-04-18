"""Environment scanning — .env files and docker-compose variants."""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import DoqlSpec, Environment
from .utils import find_compose, load_yaml


def _detect_local_env(root: Path, spec: DoqlSpec) -> None:
    """Detect local environment from .env file."""
    local_env = Environment(name="local")
    env_path = root / ".env"
    if env_path.exists():
        local_env.env_file = ".env"
        _extract_env_refs(env_path, spec)
    local_env.runtime = spec.deploy.target if spec.deploy else "docker-compose"
    spec.environments.append(local_env)


def _extract_env_refs(env_path: Path, spec: DoqlSpec) -> None:
    """Extract environment variable keys from .env file."""
    try:
        text = env_path.read_text(errors="ignore")
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key not in spec.env_refs:
                spec.env_refs.append(key)


def _detect_env_files(root: Path, spec: DoqlSpec) -> None:
    """Detect staging/prod environments from .env.* files."""
    skip_names = {"example", "local", "docker", "test", "bak"}
    for env_file in sorted(root.glob(".env.*")):
        name = env_file.name.split(".", 2)[-1]
        if name in skip_names:
            continue
        env = Environment(name=name, env_file=env_file.name)
        env.runtime = spec.deploy.target if spec.deploy else "docker-compose"
        _assign_ssh_host(env, name, spec.env_refs)
        spec.environments.append(env)


def _assign_ssh_host(env: Environment, name: str, env_refs: list[str]) -> None:
    """Assign ssh_host from env refs matching the environment name."""
    for ref in env_refs:
        if name.upper() in ref.upper() and "HOST" in ref.upper():
            env.ssh_host = f"env.{ref}"
            return


# Path patterns for docker-compose environment detection
_COMPOSE_PATTERNS: list[tuple[str, list[str]]] = [
    ("dev", ["docker-compose.dev.yml", "docker/docker-compose.dev.yml",
              "infra/docker/dev/docker-compose.dev.yml"]),
    ("staging", ["docker-compose.staging.yml", "docker/docker-compose.staging.yml"]),
    ("prod", ["docker-compose.prod.yml", "docker/docker-compose.prod.yml",
               "infra/docker/prod/docker-compose.prod.yml"]),
]


def _detect_compose_envs(root: Path, spec: DoqlSpec) -> None:
    """Detect environments from docker-compose variant files."""
    existing_names = {e.name for e in spec.environments}
    for env_name, paths in _COMPOSE_PATTERNS:
        if env_name in existing_names:
            continue
        for p in paths:
            if (root / p).exists():
                env = Environment(name=env_name, runtime="docker-compose")
                env_file = root / f".env.{env_name}"
                if env_file.exists():
                    env.env_file = env_file.name
                spec.environments.append(env)
                break


def scan_environments(root: Path, spec: DoqlSpec) -> None:
    """Detect environments from .env files and docker-compose variants."""
    _detect_local_env(root, spec)
    _detect_env_files(root, spec)
    _detect_compose_envs(root, spec)
