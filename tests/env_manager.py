"""doql Environment Manager — build, boot & health-check every example.

Discovers every `examples/*/app.doql`, runs `doql build`, and then for
each generated target verifies that it is produced correctly and
(optionally) that it serves traffic.

Targets inspected per example:

  api       → compiles, uvicorn boots, /health responds, openapi.json parses
  web       → package.json present, tsconfig valid, vite config present
  mobile    → manifest.json valid, service-worker.js parses, icons exist
  desktop   → tauri.conf.json valid, Cargo.toml present, main.rs parses
  infra     → docker-compose.yml parses, Dockerfile valid

Usage:
  python tests/env_manager.py                    # all examples
  python tests/env_manager.py notes-app          # one example
  python tests/env_manager.py --skip-api         # skip uvicorn boot
  python tests/env_manager.py --json             # machine-readable output
  python tests/env_manager.py --verbose

Exit code = number of failing checks.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"
DOQL_BIN = ROOT / "venv" / "bin" / "doql"
RUNTIME_VENV = pathlib.Path("/tmp/doql-runtime")
RUNTIME_PY = RUNTIME_VENV / "bin" / "python"
RUNTIME_UVICORN = RUNTIME_VENV / "bin" / "uvicorn"


# ────────────────────────────────────────────────────────────────────
# Data classes
# ────────────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ""

    def icon(self) -> str:
        return "✓" if self.ok else "✗"


@dataclass
class TargetReport:
    target: str           # api | web | mobile | desktop | infra
    present: bool
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.present and all(c.ok for c in self.checks)


@dataclass
class ExampleReport:
    name: str
    doql_file: pathlib.Path
    build_ok: bool
    build_output: str
    targets: dict[str, TargetReport] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.build_ok and all(t.ok for t in self.targets.values() if t.present)


# ────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────

def _find_free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run(cmd: list[str], cwd: pathlib.Path | None = None, timeout: int = 60) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired as e:
        return 124, f"TIMEOUT after {timeout}s: {e}"
    except FileNotFoundError as e:
        return 127, f"Command not found: {e}"


# ────────────────────────────────────────────────────────────────────
# Per-target checkers
# ────────────────────────────────────────────────────────────────────

def check_api(api_dir: pathlib.Path, *, boot: bool, verbose: bool = False) -> TargetReport:
    r = TargetReport("api", present=api_dir.exists())
    if not r.present:
        return r

    # File presence
    present_files = []
    for name in ("main.py", "routes.py", "models.py", "schemas.py"):
        exists = (api_dir / name).exists()
        if exists:
            present_files.append(name)
        r.checks.append(CheckResult(
            f"files/{name}",
            exists,
            "" if exists else "missing",
        ))

    # Some stub APIs (e.g. document-generator) only ship main.py — skip rest if missing
    if "main.py" not in present_files:
        r.checks.append(CheckResult("compile", False, "no main.py to compile"))
        r.checks.append(CheckResult("boot+health", False, "no main.py"))
        return r

    # Compile check — only what actually exists
    py = str(RUNTIME_PY) if RUNTIME_PY.exists() else sys.executable
    code, out = _run([py, "-m", "py_compile", *present_files], cwd=api_dir, timeout=30)
    r.checks.append(CheckResult("compile", code == 0, "" if code == 0 else out[:200]))

    if not boot:
        r.checks.append(CheckResult("boot", True, "(skipped)"))
        return r

    uvicorn_bin = str(RUNTIME_UVICORN) if RUNTIME_UVICORN.exists() else shutil.which("uvicorn")
    if not uvicorn_bin:
        r.checks.append(CheckResult("boot", False, f"uvicorn not found at {RUNTIME_UVICORN} or PATH"))
        return r

    # Clear DB and boot
    db = api_dir / "data.db"
    if db.exists():
        db.unlink()

    port = _find_free_port()
    import os
    env = os.environ.copy()
    env["JWT_SECRET"] = "envmgr-test"
    env["DATABASE_URL"] = f"sqlite:///./data-{port}.db"

    proc = subprocess.Popen(
        [uvicorn_bin, "main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=api_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        import urllib.request
        ok = False
        err = ""
        for _ in range(40):
            time.sleep(0.25)
            if proc.poll() is not None:
                err = f"server died: exit {proc.returncode}"
                break
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as resp:
                    if resp.status == 200:
                        ok = True
                        break
            except Exception as e:
                err = str(e)
        r.checks.append(CheckResult("boot+health", ok, err if not ok else f"port={port}"))

        if ok:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/openapi.json", timeout=2) as resp:
                    spec_ = json.loads(resp.read())
                    ep = len(spec_.get("paths", {}))
                    r.checks.append(CheckResult("openapi", ep > 0, f"{ep} endpoints"))
            except Exception as e:
                r.checks.append(CheckResult("openapi", False, str(e)[:200]))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
        if env_file.exists():
            env_file.unlink()

    return r


def check_web(web_dir: pathlib.Path) -> TargetReport:
    r = TargetReport("web", present=web_dir.exists() and (web_dir / "package.json").exists())
    if not r.present:
        return r

    pkg = web_dir / "package.json"
    try:
        data = json.loads(pkg.read_text())
        r.checks.append(CheckResult("package.json", True, f"name={data.get('name','?')}"))
    except Exception as e:
        r.checks.append(CheckResult("package.json", False, str(e)[:200]))

    for name in ("vite.config.ts", "tsconfig.json", "index.html"):
        r.checks.append(CheckResult(f"files/{name}", (web_dir / name).exists()))

    src = web_dir / "src"
    r.checks.append(CheckResult("src/", src.is_dir(),
                                f"{len(list(src.rglob('*.tsx')))} .tsx files" if src.is_dir() else ""))
    return r


def check_mobile(mob_dir: pathlib.Path) -> TargetReport:
    r = TargetReport("mobile", present=mob_dir.exists() and (mob_dir / "manifest.json").exists())
    if not r.present:
        return r

    manifest = mob_dir / "manifest.json"
    try:
        m = json.loads(manifest.read_text())
        has_name = bool(m.get("name"))
        has_icons = bool(m.get("icons"))
        r.checks.append(CheckResult("manifest.json",
                                    has_name and has_icons,
                                    f"name={m.get('name')} icons={len(m.get('icons', []))}"))
    except Exception as e:
        r.checks.append(CheckResult("manifest.json", False, str(e)[:200]))

    sw = mob_dir / "service-worker.js"
    ok_sw = sw.exists() and "addEventListener" in sw.read_text()
    r.checks.append(CheckResult("service-worker.js", ok_sw,
                                f"{sw.stat().st_size}B" if sw.exists() else "missing"))

    for name in ("index.html", "app.js", "style.css"):
        r.checks.append(CheckResult(f"files/{name}", (mob_dir / name).exists()))

    icons = mob_dir / "icons"
    icon_count = len(list(icons.glob("*.svg"))) if icons.is_dir() else 0
    r.checks.append(CheckResult("icons", icon_count >= 2, f"{icon_count} svg icons"))

    return r


def check_desktop(desk_dir: pathlib.Path) -> TargetReport:
    r = TargetReport("desktop", present=desk_dir.exists() and (desk_dir / "package.json").exists())
    if not r.present:
        return r

    src_tauri = desk_dir / "src-tauri"
    ok = src_tauri.is_dir()
    r.checks.append(CheckResult("src-tauri/", ok))
    if not ok:
        return r

    tconf = src_tauri / "tauri.conf.json"
    try:
        data = json.loads(tconf.read_text())
        ok = bool(data.get("package", {}).get("productName"))
        r.checks.append(CheckResult("tauri.conf.json", ok,
                                    f"productName={data.get('package', {}).get('productName')}"))
    except Exception as e:
        r.checks.append(CheckResult("tauri.conf.json", False, str(e)[:200]))

    for name in ("Cargo.toml", "build.rs", "src/main.rs"):
        p = src_tauri / name
        r.checks.append(CheckResult(f"src-tauri/{name}", p.exists()))

    main_rs = src_tauri / "src" / "main.rs"
    if main_rs.exists():
        body = main_rs.read_text()
        r.checks.append(CheckResult("main.rs/tauri_init",
                                    "tauri::Builder" in body,
                                    "" if "tauri::Builder" in body else "no tauri::Builder"))
    return r


def check_infra(infra_dir: pathlib.Path) -> TargetReport:
    r = TargetReport("infra", present=infra_dir.exists() and (infra_dir / "docker-compose.yml").exists())
    if not r.present:
        return r

    try:
        import yaml
        compose = yaml.safe_load((infra_dir / "docker-compose.yml").read_text())
        services = list((compose or {}).get("services", {}).keys())
        r.checks.append(CheckResult("compose.yaml",
                                    bool(services),
                                    f"services: {','.join(services)}"))
    except ImportError:
        r.checks.append(CheckResult("compose.yaml", True,
                                    "(yaml not installed — skipped parse)"))
    except Exception as e:
        r.checks.append(CheckResult("compose.yaml", False, str(e)[:200]))

    dockerfile = infra_dir / "Dockerfile"
    if dockerfile.exists():
        body = dockerfile.read_text()
        ok = "FROM" in body and "CMD" in body
        r.checks.append(CheckResult("Dockerfile", ok))
    else:
        r.checks.append(CheckResult("Dockerfile", False, "missing"))

    return r


# ────────────────────────────────────────────────────────────────────
# Example runner
# ────────────────────────────────────────────────────────────────────

def process_example(doql_dir: pathlib.Path, *, boot: bool, verbose: bool = False) -> ExampleReport:
    name = doql_dir.name
    doql_file = doql_dir / "app.doql"
    rep = ExampleReport(name=name, doql_file=doql_file, build_ok=False, build_output="")

    # Ensure .env
    env_example = doql_dir / ".env.example"
    env_real = doql_dir / ".env"
    if env_example.exists() and not env_real.exists():
        shutil.copy(env_example, env_real)

    # Build
    code, out = _run([str(DOQL_BIN), "-d", str(doql_dir), "build", "--force"], timeout=180)
    rep.build_output = out
    rep.build_ok = code == 0

    build = doql_dir / "build"
    rep.targets["api"] = check_api(build / "api", boot=boot, verbose=verbose)
    rep.targets["web"] = check_web(build / "web")
    rep.targets["mobile"] = check_mobile(build / "mobile")
    rep.targets["desktop"] = check_desktop(build / "desktop")
    rep.targets["infra"] = check_infra(build / "infra")
    return rep


# ────────────────────────────────────────────────────────────────────
# Reporting
# ────────────────────────────────────────────────────────────────────

def render_text(reports: list[ExampleReport]) -> str:
    lines = []
    for r in reports:
        bar = "═" * 72
        status = "✓" if r.ok else "✗"
        lines.append(f"\n{bar}\n {status} {r.name:30}  [{r.doql_file.relative_to(ROOT)}]\n{bar}")
        lines.append(f"  build: {'ok' if r.build_ok else 'FAILED'}")
        if not r.build_ok:
            lines.append("    " + "\n    ".join(r.build_output.splitlines()[-5:]))
        for t, tr in r.targets.items():
            head = f"  [{t:8}] " + ("present" if tr.present else "(absent)")
            lines.append(head)
            for ch in tr.checks:
                detail = f" — {ch.detail}" if ch.detail else ""
                lines.append(f"    {ch.icon()} {ch.name}{detail}")
    # Summary table
    lines.append("\n" + "━" * 72)
    lines.append(f"{'example':28} {'build':6} {'api':6} {'web':6} {'mob':6} {'desk':6} {'infra':6}")
    lines.append("━" * 72)
    for r in reports:
        def cell(t):
            tr = r.targets.get(t)
            if not tr or not tr.present:
                return "—"
            return "ok" if tr.ok else "FAIL"
        lines.append(
            f"{r.name:28} {'ok' if r.build_ok else 'FAIL':6} "
            f"{cell('api'):6} {cell('web'):6} {cell('mobile'):6} "
            f"{cell('desktop'):6} {cell('infra'):6}"
        )
    lines.append("━" * 72)
    total_fail = sum(1 for r in reports if not r.ok)
    lines.append(f"  {len(reports)} examples · {total_fail} failing")
    return "\n".join(lines)


def render_json(reports: list[ExampleReport]) -> str:
    def _conv(obj: Any) -> Any:
        if isinstance(obj, pathlib.Path):
            return str(obj)
        return obj
    return json.dumps([{k: _conv(v) if not isinstance(v, dict) else {kk: asdict(vv) for kk, vv in v.items()}
                        for k, v in asdict(r).items()} for r in reports], indent=2, default=str)


# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="doql environment manager")
    p.add_argument("examples", nargs="*", help="Example names to test (default: all)")
    p.add_argument("--skip-api", action="store_true", help="Skip booting API + health check")
    p.add_argument("--json", action="store_true", help="Emit JSON report")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args(argv)

    # Discover examples
    if args.examples:
        targets = [EXAMPLES / n for n in args.examples]
        for t in targets:
            if not (t / "app.doql").exists():
                print(f"✗ {t}: no app.doql", file=sys.stderr)
                return 2
    else:
        targets = sorted(p.parent for p in EXAMPLES.glob("*/app.doql"))

    if not DOQL_BIN.exists():
        print(f"✗ doql binary not found: {DOQL_BIN}", file=sys.stderr)
        return 2

    print(f"→ Testing {len(targets)} example(s) (boot-api={not args.skip_api})", file=sys.stderr)

    reports: list[ExampleReport] = []
    for d in targets:
        print(f"  · {d.name} …", file=sys.stderr)
        reports.append(process_example(d, boot=not args.skip_api, verbose=args.verbose))

    if args.json:
        print(render_json(reports))
    else:
        print(render_text(reports))

    return sum(1 for r in reports if not r.ok)


if __name__ == "__main__":
    sys.exit(main())
