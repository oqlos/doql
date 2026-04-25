"""Remote SSH diagnostics for the doctor command."""
from __future__ import annotations

import subprocess

from ....parsers.models import DoqlSpec
from .report import DoctorReport


def _ssh_run(host: str, cmd: str | list[str]) -> tuple[int, str, str] | None:
    """Run an SSH command; return (returncode, stdout, stderr) or None on timeout/not-found."""
    if isinstance(cmd, str):
        remote_args = [cmd]
    else:
        remote_args = cmd
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", host] + remote_args,
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _check_remote_ssh(host: str, report: DoctorReport) -> bool:
    """Check SSH connectivity; returns True if reachable."""
    res = _ssh_run(host, ["echo", "ok"])
    if res is None:
        report.add("remote:ssh", "fail", f"SSH to {host} timed out / ssh not found")
        return False
    rc, _, stderr = res
    if rc != 0:
        report.add("remote:ssh", "fail", f"SSH to {host} failed: {stderr}")
        return False
    report.add("remote:ssh", "ok", f"SSH to {host} reachable")
    return True


def _check_remote_runtime(host: str, runtime: str, report: DoctorReport) -> None:
    check_cmd = "podman --version" if runtime in ("quadlet", "podman") else "docker --version"
    res = _ssh_run(host, check_cmd)
    if res is None:
        report.add("remote:runtime", "warn", "Could not check remote runtime")
    elif res[0] == 0:
        report.add("remote:runtime", "ok", res[1])
    else:
        report.add("remote:runtime", "warn", f"{check_cmd} not available on remote")


def _check_remote(spec: DoqlSpec, env_name: str, report: DoctorReport) -> None:
    """Run remote diagnostics via SSH for a specific environment."""
    env = next((e for e in spec.environments if e.name == env_name), None)
    if not env:
        report.add("remote", "fail", f"Environment '{env_name}' not found")
        return
    if not env.ssh_host:
        report.add("remote", "skip", f"No ssh_host for '{env_name}'")
        return

    if not _check_remote_ssh(env.ssh_host, report):
        return
    _check_remote_runtime(env.ssh_host, env.runtime, report)

    res = _ssh_run(env.ssh_host, "df -h / | tail -1 | awk '{print $4}'")
    if res is not None and res[0] == 0:
        report.add("remote:disk", "ok", f"Free space: {res[1]}")
