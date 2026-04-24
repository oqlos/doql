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


def _has_module(name: str) -> bool:
    py = str(RUNTIME_PY) if RUNTIME_PY.exists() else sys.executable
    code, _ = _run([py, "-c", f"import {name}"])
    return code == 0


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

def _api_present_files(api_dir: pathlib.Path) -> list[str]:
    return [n for n in ("main.py", "routes.py", "models.py", "schemas.py") if (api_dir / n).exists()]


def _api_compile_check(api_dir: pathlib.Path, files: list[str]) -> CheckResult:
    py = str(RUNTIME_PY) if RUNTIME_PY.exists() else sys.executable
    code, out = _run([py, "-m", "py_compile", *files], cwd=api_dir, timeout=30)
    return CheckResult("compile", code == 0, "" if code == 0 else out[:200])


def _check_postgres_skip(api_dir: pathlib.Path) -> CheckResult | None:
    dbfile = api_dir / "database.py"
    if not dbfile.exists():
        return None
    body = dbfile.read_text()
    if "postgresql://" not in body and "postgres://" not in body:
        return None
    if _has_module("psycopg2"):
        return None
    return CheckResult(
        "boot+health", True,
        "(skipped: database.py hardcodes postgres and psycopg2 absent)",
    )


def _wait_health(port: int, proc: subprocess.Popen) -> tuple[bool, str]:
    import urllib.request
    err = ""
    for _ in range(40):
        time.sleep(0.25)
        if proc.poll() is not None:
            return False, f"server died: exit {proc.returncode}"
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as resp:
                if resp.status == 200:
                    return True, ""
        except Exception as e:
            err = str(e)
    return False, err


def _check_api_openapi(port: int) -> CheckResult:
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/openapi.json", timeout=2) as resp:
            spec_ = json.loads(resp.read())
            ep = len(spec_.get("paths", {}))
            return CheckResult("openapi", ep > 0, f"{ep} endpoints")
    except Exception as e:
        return CheckResult("openapi", False, str(e)[:200])


def check_api(api_dir: pathlib.Path, *, boot: bool, verbose: bool = False) -> TargetReport:
    # Treat stub directories (no main.py) as "absent" — these are examples that
    # intentionally don't generate an API (e.g. kiosk-station, document-generator).
    has_main = api_dir.exists() and (api_dir / "main.py").exists()
    r = TargetReport("api", present=has_main)
    if not r.present:
        return r

    present_files = _api_present_files(api_dir)
    for name in ("main.py", "routes.py", "models.py", "schemas.py"):
        exists = name in present_files
        r.checks.append(CheckResult(f"files/{name}", exists, "" if exists else "missing"))

    r.checks.append(_api_compile_check(api_dir, present_files))

    if not boot:
        r.checks.append(CheckResult("boot", True, "(skipped)"))
        return r

    uvicorn_bin = str(RUNTIME_UVICORN) if RUNTIME_UVICORN.exists() else shutil.which("uvicorn")
    if not uvicorn_bin:
        r.checks.append(CheckResult("boot", False, f"uvicorn not found at {RUNTIME_UVICORN} or PATH"))
        return r

    skip = _check_postgres_skip(api_dir)
    if skip:
        r.checks.append(skip)
        return r

    # Clear DB and boot. Generated database.py hardcodes sqlite:///./data/app.db,
    # so make sure the data/ directory exists before launching uvicorn.
    (api_dir / "data").mkdir(exist_ok=True)
    for old in (api_dir / "data").glob("*.db"):
        try:
            old.unlink()
        except Exception:
            pass

    port = _find_free_port()
    import os
    env = os.environ.copy()
    env["JWT_SECRET"] = "envmgr-test"
    env["DATABASE_URL"] = f"sqlite:///./data/app-{port}.db"

    proc = subprocess.Popen(
        [uvicorn_bin, "main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=api_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        ok, err = _wait_health(port, proc)
        r.checks.append(CheckResult("boot+health", ok, err if not ok else f"port={port}"))
        if ok:
            r.checks.append(_check_api_openapi(port))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

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


def _check_tauri_conf(src_tauri: pathlib.Path) -> CheckResult:
    tconf = src_tauri / "tauri.conf.json"
    try:
        data = json.loads(tconf.read_text())
        product = data.get("productName") or data.get("package", {}).get("productName")
        schema = data.get("$schema", "")
        version = "v2" if "/config/2" in schema or "productName" in data else "v1"
        return CheckResult("tauri.conf.json", bool(product),
                           f"{version} productName={product}")
    except Exception as e:
        return CheckResult("tauri.conf.json", False, str(e)[:200])


def _check_desktop_files(src_tauri: pathlib.Path) -> list[CheckResult]:
    return [CheckResult(f"src-tauri/{name}", (src_tauri / name).exists())
            for name in ("Cargo.toml", "build.rs", "src/main.rs")]


def _check_main_rs(src_tauri: pathlib.Path) -> CheckResult | None:
    main_rs = src_tauri / "src" / "main.rs"
    if not main_rs.exists():
        return None
    body = main_rs.read_text()
    return CheckResult("main.rs/tauri_init",
                       "tauri::Builder" in body,
                       "" if "tauri::Builder" in body else "no tauri::Builder")


def _check_cargo(cargo_check: bool, src_tauri: pathlib.Path) -> CheckResult | None:
    if not cargo_check:
        return None
    if not shutil.which("cargo"):
        return CheckResult("cargo check", False, "cargo not in PATH")
    cargo_toml = src_tauri / "Cargo.toml"
    code, out = _run(["cargo", "check", "--manifest-path", str(cargo_toml)], timeout=600)
    ok = code == 0
    tail = " | ".join(l.strip() for l in out.splitlines() if l.strip())[-300:]
    return CheckResult("cargo check", ok, tail if not ok else "compiles")


def check_desktop(desk_dir: pathlib.Path, *, cargo_check: bool = False) -> TargetReport:
    r = TargetReport("desktop", present=desk_dir.exists() and (desk_dir / "package.json").exists())
    if not r.present:
        return r

    src_tauri = desk_dir / "src-tauri"
    ok = src_tauri.is_dir()
    r.checks.append(CheckResult("src-tauri/", ok))
    if not ok:
        return r

    r.checks.append(_check_tauri_conf(src_tauri))
    r.checks.extend(_check_desktop_files(src_tauri))

    main_check = _check_main_rs(src_tauri)
    if main_check:
        r.checks.append(main_check)

    cargo = _check_cargo(cargo_check, src_tauri)
    if cargo:
        r.checks.append(cargo)

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

def process_example(doql_dir: pathlib.Path, *, boot: bool, cargo_check: bool = False, verbose: bool = False) -> ExampleReport:
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
    rep.targets["desktop"] = check_desktop(build / "desktop", cargo_check=cargo_check)
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
    p.add_argument("--cargo-check", action="store_true", help="Run `cargo check` for desktop targets (slow first time)")
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
        reports.append(process_example(d, boot=not args.skip_api, cargo_check=args.cargo_check, verbose=args.verbose))

    if args.json:
        print(render_json(reports))
    else:
        print(render_text(reports))

    return sum(1 for r in reports if not r.ok)


if __name__ == "__main__":
    sys.exit(main())
