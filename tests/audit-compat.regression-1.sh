#!/usr/bin/env bash
# audit-compat.regression-1.sh — V1 契约夹具 + smoke-write
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIX="$ROOT/tests/fixtures/audit-v1-wiki"
PY="${PYTHON_CMD:-python}"

if ! command -v "$PY" >/dev/null 2>&1; then
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  else
    echo "FAIL: no python" >&2
    exit 1
  fi
fi

[ -d "$FIX" ] || { echo "FAIL: missing fixture $FIX" >&2; exit 1; }
[ -f "$FIX/audit/20260101-120000-gold-shape.md" ] || {
  echo "FAIL: missing gold open audit" >&2
  exit 1
}
[ -f "$ROOT/references/audit-contract-v1.md" ] || {
  echo "FAIL: missing contract doc" >&2
  exit 1
}

echo "=== check fixture shape ==="
"$PY" "$ROOT/scripts/check-audit-compat.py" "$FIX"

echo "=== smoke-write obsidian-plugin ==="
"$PY" "$ROOT/scripts/check-audit-compat.py" "$FIX" --smoke-write

echo "PASS: audit-compat regression"
