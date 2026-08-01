#!/usr/bin/env bash
# graph-audit-panel.regression-1.sh — V5: offline HTML embeds audit panel
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIX="$ROOT/tests/fixtures/graph-interactive-basic"
TMP="${TMPDIR:-/tmp}/llm-wiki-v5-graph-$$"
PY="${PYTHON_CMD:-python}"
command -v "$PY" >/dev/null 2>&1 || PY=python3

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

mkdir -p "$TMP/wiki"
cp "$FIX/wiki/graph-data.json" "$TMP/wiki/graph-data.json"

# ensure engine exists for build-graph-html
if [ ! -f "$ROOT/skill-assets/graph-engine/dist/engine.iife.js" ] && [ ! -f "$ROOT/packages/graph-engine/dist/engine.iife.js" ]; then
  echo "SKIP: no engine.iife.js (install/build graph-engine first)" >&2
  exit 0
fi

bash "$ROOT/scripts/build-graph-html.sh" "$TMP"
HTML="$TMP/wiki/knowledge-graph.html"
[ -f "$HTML" ] || { echo "FAIL: no knowledge-graph.html" >&2; exit 1; }

grep -q "LlmWikiGraphAuditPanel" "$HTML" || {
  echo "FAIL: HTML missing LlmWikiGraphAuditPanel" >&2
  exit 1
}
grep -q "offline-audit-btn" "$HTML" || {
  echo "FAIL: HTML missing offline-audit-btn mount" >&2
  exit 1
}
grep -q "记批注" "$HTML" || {
  echo "FAIL: HTML missing 记批注 label" >&2
  exit 1
}
grep -q "onSelectionChange" "$HTML" || {
  echo "FAIL: HTML missing onSelectionChange wiring" >&2
  exit 1
}

node --test "$ROOT/tests/js/graph-audit-panel.test.mjs"

echo "PASS: graph-audit-panel regression"
