"""Deployment scanning — Docker, docker-compose, quadlet, ansible."""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import DoqlSpec, Deploy
from .utils import find_compose, find_dockerfiles, load_yaml


def scan_deploy(root: Path, spec: DoqlSpec) -> None:
    """Detect deployment infrastructure."""
    compose = find_compose(root)
    has_dockerfile = find_dockerfiles(root)
    has_quadlet = (root / "infra" / "quadlet").is_dir() or \
                  (root / "deploy" / "quadlet").is_dir()
    has_ansible = any((root / d).is_dir() for d in ("ansible", "deploy/ansible", "infra/ansible"))
    has_makefile = (root / "Makefile").exists()

    deploy = Deploy()

    if compose:
        deploy.target = "docker-compose"
        deploy.config["compose_file"] = str(compose.relative_to(root))
    elif has_dockerfile:
        deploy.target = "docker"
    elif has_quadlet:
        deploy.target = "podman-quadlet"
    elif has_makefile:
        deploy.target = "makefile"

    if has_quadlet:
        deploy.config["quadlet"] = True
    if has_ansible:
        deploy.config["ansible"] = True

    # Detect rootless podman
    for ref in spec.env_refs:
        if "ROOTLESS" in ref.upper():
            deploy.rootless = True
            break

    # Detect services from docker-compose
    if compose:
        data = load_yaml(compose)
        if data:
            services = data.get("services", {})
            for svc_name, svc in services.items():
                image = svc.get("image", "")
                build = svc.get("build")
                ports = svc.get("ports", [])
                # Skip databases (already scanned)
                if any(db in image for db in ("postgres", "mysql", "redis", "mongo")):
                    continue
                container = {"name": svc_name}
                if image:
                    container["image"] = image
                if build:
                    container["build"] = build if isinstance(build, str) else build.get("context", ".")
                if ports:
                    container["ports"] = ports
                deploy.containers.append(container)

    spec.deploy = deploy
