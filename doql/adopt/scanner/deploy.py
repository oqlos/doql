"""Deployment scanning — Docker, docker-compose, quadlet, ansible."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ...parsers.models import DoqlSpec, Deploy
from .utils import find_compose, find_dockerfiles, load_yaml


# Database images to skip when extracting containers
_DB_IMAGES = ("postgres", "mysql", "redis", "mongo")


def _detect_deployment_indicators(root: Path) -> dict[str, Any]:
    """Detect deployment infrastructure indicators."""
    return {
        "compose": find_compose(root),
        "has_dockerfile": bool(find_dockerfiles(root)),
        "has_quadlet": (root / "infra" / "quadlet").is_dir() or
                       (root / "deploy" / "quadlet").is_dir(),
        "has_ansible": any((root / d).is_dir()
                          for d in ("ansible", "deploy/ansible", "infra/ansible")),
        "has_makefile": (root / "Makefile").exists(),
    }


def _determine_deploy_target(indicators: dict[str, Any], deploy: Deploy, root: Path) -> None:
    """Set deployment target based on detected indicators."""
    compose = indicators["compose"]
    if compose:
        deploy.target = "docker-compose"
        deploy.config["compose_file"] = str(compose.relative_to(root))
    elif indicators["has_dockerfile"]:
        deploy.target = "docker"
    elif indicators["has_quadlet"]:
        deploy.target = "podman-quadlet"
    elif indicators["has_makefile"]:
        deploy.target = "makefile"


def _apply_deploy_config_flags(indicators: dict[str, Any], deploy: Deploy) -> None:
    """Apply boolean config flags based on indicators."""
    if indicators["has_quadlet"]:
        deploy.config["quadlet"] = True
    if indicators["has_ansible"]:
        deploy.config["ansible"] = True


def _is_database_service(image: str) -> bool:
    """Check if service image is a known database."""
    return any(db in image for db in _DB_IMAGES)


def _extract_container_config(svc_name: str, svc: dict[str, Any]) -> dict[str, Any]:
    """Extract container configuration from compose service."""
    image = svc.get("image", "")
    build = svc.get("build")
    ports = svc.get("ports", [])

    container: dict[str, Any] = {"name": svc_name}
    if image:
        container["image"] = image
    if build:
        container["build"] = build if isinstance(build, str) else build.get("context", ".")
    if ports:
        container["ports"] = ports
    return container


def _extract_containers_from_compose(compose: Path | None, deploy: Deploy) -> None:
    """Extract non-database containers from docker-compose."""
    if not compose:
        return

    data = load_yaml(compose)
    if not data:
        return

    services = data.get("services", {})
    for svc_name, svc in services.items():
        image = svc.get("image", "")
        if _is_database_service(image):
            continue
        container = _extract_container_config(svc_name, svc)
        deploy.containers.append(container)


def _detect_rootless(spec: DoqlSpec) -> bool:
    """Detect rootless podman from env refs."""
    return any("ROOTLESS" in ref.upper() for ref in spec.env_refs)


def scan_deploy(root: Path, spec: DoqlSpec) -> None:
    """Detect deployment infrastructure."""
    indicators = _detect_deployment_indicators(root)
    deploy = Deploy()

    _determine_deploy_target(indicators, deploy, root)
    _apply_deploy_config_flags(indicators, deploy)

    if _detect_rootless(spec):
        deploy.rootless = True

    _extract_containers_from_compose(indicators["compose"], deploy)

    spec.deploy = deploy
