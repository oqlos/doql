"""Generate docker-compose / quadlet / kiosk / k8s / terraform / nginx infra from DoqlSpec.

Produces:
  infra/
  ├── docker-compose.yml    — full compose with api + traefik + db
  ├── Dockerfile            — multi-stage Python build
  ├── .env.docker           — env vars for compose
  └── traefik.yml           — static Traefik config  (if traefik=true)

Or for quadlet:
  infra/
  ├── <app>.container        — Podman Quadlet unit
  ├── <app>-traefik.container
  └── <app>.env

Or for kiosk-appliance:
  infra/
  ├── install-kiosk.sh       — full installer (Openbox + Chromium + systemd)
  └── kiosk.service
"""
from __future__ import annotations

import pathlib

from ...parser import DoqlSpec
from ...utils.naming import slug
from .docker import _gen_docker_compose
from .quadlet import _gen_quadlet
from .kiosk import _gen_kiosk
from .kubernetes import _gen_kubernetes
from .terraform import _gen_terraform
from .nginx import _gen_nginx
from .migration import _gen_migration_spec


def _map_deploy_strategy(doql_target: str) -> str:
    """Map doql DEPLOY.target to redeploy DeployStrategy value."""
    return {
        "docker-compose": "docker_full",
        "quadlet":        "podman_quadlet",
        "kubernetes":     "k3s",
        "kiosk-appliance": "podman_quadlet",
        "systemd":        "systemd",
    }.get(doql_target, "docker_full")


def generate(spec: DoqlSpec, env_vars: dict[str, str], out: pathlib.Path) -> None:
    """Generate infra layer files into *out* directory."""
    # Prefer explicit Infrastructure blocks over legacy deploy.target
    infra_types = {i.type for i in spec.infrastructures}
    ingress_types = {i.type for i in spec.ingresses}

    # Fallback to legacy deploy.target if no Infrastructure blocks declared
    if not infra_types:
        infra_types = {spec.deploy.target}
    # Also include legacy docker target so docker-compose still emits
    # alongside new Infrastructure blocks (backward compat)
    elif spec.deploy.target in ("docker", "docker-compose"):
        infra_types.add("docker-compose")

    for itype in infra_types:
        if itype in ("docker-compose", "docker"):
            _gen_docker_compose(spec, env_vars, out)
        elif itype == "quadlet":
            _gen_quadlet(spec, env_vars, out)
        elif itype == "kiosk-appliance":
            _gen_kiosk(spec, env_vars, out)
        elif itype in ("kubernetes", "k8s", "k3s"):
            _gen_kubernetes(spec, env_vars, out)
        elif itype == "terraform":
            _gen_terraform(spec, env_vars, out)
        else:
            _gen_docker_compose(spec, env_vars, out)

    # Nginx config if requested via Ingress block
    if "nginx" in ingress_types:
        _gen_nginx(spec, env_vars, out)

    # Always emit migration.yaml for redeploy (doql[deploy])
    _gen_migration_spec(spec, env_vars, out)
