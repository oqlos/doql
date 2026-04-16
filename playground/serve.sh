#!/usr/bin/env bash
# Serve the doql playground locally on :8088.
# Refreshes the bundled wheel from ../dist/ first.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"

# Refresh wheel (if a newer one exists in ../dist/)
if ls "$REPO/dist"/doql-*.whl >/dev/null 2>&1; then
  cp "$REPO/dist"/doql-*.whl "$HERE/"
  echo "✓ wheel refreshed"
fi

echo "→ http://127.0.0.1:8088/"
exec python3 -m http.server -d "$HERE" 8088
