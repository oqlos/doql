#!/usr/bin/env bash
# Boot every example's generated API and verify /health + OpenAPI responds.
# Catches regressions across all generator paths, not just asset-management.
set -eo pipefail

ROOT="/home/tom/github/oqlos/doql"
VENV="/tmp/doql-runtime"
PORT=8777

# Examples that produce an API (have ENTITY definitions). kiosk-station
# and document-generator may only have documents/interfaces — they are
# skipped when no api/main.py exists.
EXAMPLES=(
  asset-management
  calibration-lab
  iot-fleet
  document-generator
  kiosk-station
)

cleanup() {
  pkill -f "uvicorn main:app.*--port $PORT" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

pass=0
skip=0
fail=0

for ex in "${EXAMPLES[@]}"; do
  api_dir="$ROOT/examples/$ex/build/api"
  printf "\n── %-22s  " "$ex"

  # Ensure fresh build
  "$ROOT/venv/bin/doql" -d "$ROOT/examples/$ex" build --force >/dev/null 2>&1 || {
    echo "✗ build failed"; fail=$((fail+1)); continue
  }

  if [[ ! -f "$api_dir/main.py" ]]; then
    echo "— (no API generated, skipped)"
    skip=$((skip+1))
    continue
  fi

  # Compile the API as a sanity check (catches syntax errors)
  (cd "$api_dir" && "$VENV/bin/python" -m py_compile main.py routes.py models.py schemas.py) || {
    echo "✗ .py compile failed"; fail=$((fail+1)); continue
  }

  # Boot server
  rm -f "$api_dir/data.db"
  cleanup; sleep 0.3
  (cd "$api_dir" && JWT_SECRET=test-secret "$VENV/bin/uvicorn" main:app \
    --host 127.0.0.1 --port $PORT > /tmp/doql-ex-${ex}.log 2>&1) &
  server_pid=$!

  # Wait
  ready=0
  for i in $(seq 1 40); do
    sleep 0.25
    if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      ready=1
      break
    fi
    kill -0 $server_pid 2>/dev/null || break
  done

  if [[ $ready -eq 0 ]]; then
    echo "✗ did not become ready"
    tail -5 /tmp/doql-ex-${ex}.log | sed 's/^/        /'
    fail=$((fail+1))
    kill $server_pid 2>/dev/null || true
    continue
  fi

  # Verify OpenAPI schema
  endpoints=$(curl -sf "http://127.0.0.1:$PORT/openapi.json" | \
    "$VENV/bin/python" -c "import sys,json; print(len(json.load(sys.stdin)['paths']))")
  echo "✓ /health OK  |  $endpoints endpoints"

  kill $server_pid 2>/dev/null || true
  wait $server_pid 2>/dev/null || true
  pass=$((pass+1))
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  passed: $pass    skipped: $skip    failed: $fail"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit $fail
