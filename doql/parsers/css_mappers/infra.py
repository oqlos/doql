"""Infrastructure, deploy, database, environment, ingress, and CI mappers."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec
    from ..css_utils import CssBlock, ParsedSelector


def _map_deploy(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Deploy definition."""
    from ..models import Deploy
    deploy = Deploy(
        target=block.declarations.get('target', ''),
    )
    for key, val in block.declarations.items():
        if key.startswith('@'):
            deploy.directives[key[1:]] = val
        else:
            deploy.config[key] = val
    spec.deploy = deploy


def _map_database(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Database definition."""
    from ..models import Database
    name = sel.attributes.get('name', '')
    db = Database(
        name=name,
        type=block.declarations.get('type', ''),
        url=block.declarations.get('url', ''),
    )
    spec.databases.append(db)


def _map_environment(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Environment definition."""
    from ..models import Environment
    name = sel.attributes.get('name', '')
    if not name:
        return
    env = Environment(
        name=name,
        runtime=block.declarations.get('runtime', 'docker-compose'),
    )
    env.env_file = block.declarations.get('env_file')
    env.ssh_host = block.declarations.get('ssh_host')
    replicas = block.declarations.get('replicas')
    if replicas and replicas.isdigit():
        env.replicas = int(replicas)
    # Store remaining declarations as config
    skip = {'runtime', 'env_file', 'ssh_host', 'replicas'}
    for k, v in block.declarations.items():
        if k not in skip:
            env.config[k] = v
    spec.environments.append(env)


def _map_infrastructure(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Infrastructure definition (Kubernetes, Terraform, Docker)."""
    from ..models import Infrastructure
    name = sel.attributes.get('name', '')
    infra = Infrastructure(
        name=name,
        type=sel.attributes.get('type', 'docker-compose'),
        provider=block.declarations.get('provider'),
        namespace=block.declarations.get('namespace'),
    )
    replicas = block.declarations.get('replicas')
    if replicas and replicas.isdigit():
        infra.replicas = int(replicas)
    skip = {'provider', 'namespace', 'replicas'}
    for k, v in block.declarations.items():
        if k not in skip:
            infra.config[k] = v
    spec.infrastructures.append(infra)


def _map_ingress(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Ingress definition (Nginx, Traefik)."""
    from ..models import Ingress
    name = sel.attributes.get('name', '')
    ingress = Ingress(
        name=name,
        type=sel.attributes.get('type', 'traefik'),
        tls=block.declarations.get('tls', '').lower() == 'true',
        cert_manager=block.declarations.get('cert_manager'),
        rate_limit=block.declarations.get('rate_limit'),
    )
    skip = {'tls', 'cert_manager', 'rate_limit'}
    for k, v in block.declarations.items():
        if k not in skip:
            ingress.config[k] = v
    spec.ingresses.append(ingress)


def _map_ci(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to CI/CD config (GitHub, GitLab, Jenkins)."""
    from ..models import CiConfig
    from ..css_utils import _parse_list
    name = sel.attributes.get('name', '')
    ci = CiConfig(
        name=name,
        type=sel.attributes.get('type', 'github'),
        runner=block.declarations.get('runner'),
    )
    stages_str = block.declarations.get('stages')
    if stages_str:
        ci.stages = _parse_list(stages_str)
    skip = {'runner', 'stages'}
    for k, v in block.declarations.items():
        if k not in skip:
            ci.config[k] = v
    spec.ci_configs.append(ci)
