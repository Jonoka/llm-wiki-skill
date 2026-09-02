#!/usr/bin/env bash
# audit-compat.regression-1.sh — V1 契约夹具 + smoke-write
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIX="$ROOT/tests/fixtures/audit-v1-wiki"
PY="${PYTHON_CMD:-python}"
TMP="${TMPDIR:-/tmp}/llm-wiki-audit-compat-$$"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

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

echo "=== reject traversal and absolute producer targets ==="
mkdir -p "$TMP/producer"
cp -R "$FIX/." "$TMP/producer/"
open_before="$(find "$TMP/producer/audit" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
if "$PY" "$ROOT/scripts/audit-file.py" "$TMP/producer" \
  --target 'wiki/../../../../SKILL.md' --anchor-text x --comment x; then
  echo "FAIL: audit-file accepted a traversal target" >&2
  exit 1
fi
if "$PY" "$ROOT/scripts/audit-file.py" "$TMP/producer" \
  --target "$ROOT/SKILL.md" --anchor-text x --comment x; then
  echo "FAIL: audit-file accepted an absolute target" >&2
  exit 1
fi
if "$PY" "$ROOT/scripts/audit-file.py" "$TMP/producer" \
  --target 'purpose.md' --anchor-text x --comment x; then
  echo "FAIL: audit-file accepted a non-wiki target" >&2
  exit 1
fi
open_after="$(find "$TMP/producer/audit" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
[ "$open_before" = "$open_after" ] || { echo "FAIL: rejected producer target wrote an audit" >&2; exit 1; }

echo "=== checker and reviewer fail closed on invalid contract ==="
mkdir -p "$TMP/invalid"
cp -R "$FIX/." "$TMP/invalid/"
invalid="$TMP/invalid/audit/20260101-120000-gold-shape.md"
sed -i \
  -e 's|target: wiki/entities/SampleConcept.md|target: wiki/../../../../SKILL.md\nextra_field: forbidden|' \
  -e 's|severity: warn|severity: warn\nseverity: info|' \
  -e 's|created: 2026-01-01T12:00:00+08:00|created: definitely-not-iso|' \
  "$invalid"
if "$PY" "$ROOT/scripts/check-audit-compat.py" "$TMP/invalid"; then
  echo "FAIL: checker accepted traversal/extra/duplicate/invalid-created" >&2
  exit 1
fi
if "$PY" "$ROOT/scripts/audit-review.py" "$TMP/invalid" --open; then
  echo "FAIL: audit-review exited 0 on invalid contract" >&2
  exit 1
fi

echo "PASS: audit-compat regression"
