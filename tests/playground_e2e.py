"""Headless end-to-end test for the playground.

Serves `playground/` on a local port, launches Chromium via Playwright,
waits for Pyodide to finish booting, and verifies that the editor +
diagnostics pipeline actually works.
"""
from __future__ import annotations

import http.server
import os
import pathlib
import socketserver
import sys
import threading
import time
from contextlib import contextmanager


ROOT = pathlib.Path(__file__).parent.parent
PLAYGROUND = ROOT / "playground"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_a):
        pass


@contextmanager
def serve():
    os.chdir(PLAYGROUND)
    # Bind to an ephemeral port so re-runs don't collide.
    with socketserver.TCPServer(("127.0.0.1", 0), _QuietHandler) as httpd:
        port = httpd.server_address[1]
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{port}/"
        finally:
            httpd.shutdown()


def main() -> int:
    from playwright.sync_api import sync_playwright

    with serve() as url, sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()

        console_errors: list[str] = []

        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", on_console)
        page.goto(url, wait_until="domcontentloaded")

        print(f"→ loaded {url}")

        # Wait for Pyodide to finish booting (status = Ready). Takes ~15-30s cold.
        print("  waiting for Pyodide to boot (up to 60s)…")
        page.wait_for_selector("#status.status-ready", timeout=60_000)
        print("  ✓ pyodide ready")

        # Verify the version shows up
        version = page.locator("#doql-version").inner_text()
        assert version and version != "…", f"version not populated: {version!r}"
        print(f"  ✓ doql version label: {version}")

        # Auto-build should have populated the diagnostics / models.py panes.
        # Wait for the "No issues" banner OR at least one diagnostic row.
        page.wait_for_selector(".no-diagnostics, .diagnostic", timeout=15_000)

        # Switch to models.py tab and verify it's non-empty
        page.click('button[data-tab="models"]')
        models_text = page.locator("#models-view").inner_text()
        assert "class User(Base)" in models_text, f"models.py missing User class:\n{models_text[:200]}"
        assert "class Task(Base)" in models_text, f"models.py missing Task class"
        print(f"  ✓ models.py generated ({len(models_text)} chars)")

        # Switch to AST tab
        page.click('button[data-tab="ast"]')
        ast_text = page.locator("#ast-view").inner_text()
        assert '"app_name": "My App"' in ast_text, f"AST missing app_name:\n{ast_text[:200]}"
        print(f"  ✓ AST renders correctly")

        # Now type something broken to verify live diagnostics
        page.click('button[data-tab="diagnostics"]')
        page.locator("#editor").fill(
            'APP: "Broken"\nENTITY Foo:\n  bar: NonExistent ref\n'
        )
        # Wait for the debounce + rebuild
        page.wait_for_timeout(800)

        diag_text = page.locator("#diagnostics").inner_text()
        assert "NonExistent" in diag_text, f"broken input didn't yield error:\n{diag_text}"
        print(f"  ✓ live rebuild shows dangling-ref error")

        # No console errors except dev-time warnings
        fatal = [e for e in console_errors if "Could not install" not in e]
        if fatal:
            print(f"  ✗ unexpected console errors: {fatal}")
            return 1

        # Restore the initial example for a clean screenshot
        page.locator("#example-picker").select_option("minimal")
        page.wait_for_timeout(800)
        page.click('button[data-tab="diagnostics"]')
        page.wait_for_timeout(300)

        screenshot = ROOT / "playground" / "screenshot.png"
        page.screenshot(path=str(screenshot), full_page=False)
        print(f"  ✓ screenshot → {screenshot.relative_to(ROOT)}")

        print("\n🎉 PLAYGROUND E2E PASSED 🎉")

        browser.close()
        return 0


if __name__ == "__main__":
    sys.exit(main())
