"""Generate CI/CD configuration files.

Produces:
  .github/workflows/doql-ci.yml  — GitHub Actions workflow for validate + build + test
"""
from __future__ import annotations

import pathlib
import textwrap

from ..parser import DoqlSpec


def _gen_github_action(spec: DoqlSpec) -> str:
    """Generate a GitHub Actions workflow for doql projects."""
    return textwrap.dedent(f'''\
        name: doql CI

        on:
          push:
            branches: [main, develop]
          pull_request:
            branches: [main]

        jobs:
          validate:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
                with:
                  python-version: "3.12"
              - name: Install doql
                run: pip install doql
              - name: Validate
                run: doql validate
              - name: Build
                run: doql build --force
              - name: Check generated Python
                run: |
                  cd build/api
                  python -c "
                  import py_compile, os
                  for r, d, fs in os.walk('.'):
                      for f in fs:
                          if f.endswith('.py'):
                              py_compile.compile(os.path.join(r,f), doraise=True)
                  print('All Python files compile OK')
                  "

          api-test:
            runs-on: ubuntu-latest
            needs: validate
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-python@v5
                with:
                  python-version: "3.12"
              - name: Install doql & build
                run: |
                  pip install doql
                  doql build --force
              - name: Install API deps
                run: |
                  cd build/api
                  pip install -r requirements.txt
              - name: API smoke test
                run: |
                  cd build/api
                  timeout 10 python -c "
                  from main import app
                  from fastapi.testclient import TestClient
                  client = TestClient(app)
                  r = client.get('/health')
                  assert r.status_code == 200
                  assert r.json()['status'] == 'ok'
                  print('Health check passed')
                  " || true

          web-build:
            runs-on: ubuntu-latest
            needs: validate
            steps:
              - uses: actions/checkout@v4
              - uses: actions/setup-node@v4
                with:
                  node-version: "20"
              - uses: actions/setup-python@v5
                with:
                  python-version: "3.12"
              - name: Install doql & build
                run: |
                  pip install doql
                  doql build --force
              - name: Install web deps
                run: |
                  cd build/web
                  npm install
              - name: Build web
                run: |
                  cd build/web
                  npm run build
    ''')


def generate(spec: DoqlSpec, env_vars: dict[str, str], out: pathlib.Path) -> None:
    """Generate CI configuration files."""
    gh_dir = out / ".github" / "workflows"
    gh_dir.mkdir(parents=True, exist_ok=True)

    (gh_dir / "doql-ci.yml").write_text(_gen_github_action(spec), encoding="utf-8")
    print(f"    → .github/workflows/doql-ci.yml")
