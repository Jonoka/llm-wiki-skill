#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FIX="$ROOT/tests/fixtures/audit-v1-wiki"
PY="${PYTHON_CMD:-python}"
TMP="${TMPDIR:-/tmp}/llm-wiki-audit-resolve-$$"
AUDIT_ID="20260101-120000-a1b2"
AUDIT_NAME="20260101-120000-gold-shape.md"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT
command -v "$PY" >/dev/null 2>&1 || PY=python3

make_replacement() {
  sed 's/知识库纠错应写入 audit 目录而不是只留在聊天里。/知识库纠错必须保留可恢复的 audit 记录。/' \
    "$1/wiki/entities/SampleConcept.md" > "$2"
}

echo "=== collision is archived without clobber ==="
mkdir -p "$TMP/collision"
cp -R "$FIX/." "$TMP/collision/"
cp "$TMP/collision/audit/$AUDIT_NAME" "$TMP/collision/audit/resolved/$AUDIT_NAME"
sed -i \
  -e 's/id: 20260101-120000-a1b2/id: 20260101-120000-cafe/' \
  -e 's/status: open/status: resolved/' \
  "$TMP/collision/audit/resolved/$AUDIT_NAME"
make_replacement "$TMP/collision" "$TMP/collision-replacement.md"
"$PY" "$ROOT/scripts/audit-resolve.py" "$TMP/collision" "audit/$AUDIT_NAME" \
  --outcome accept --summary "collision test" --replacement-file "$TMP/collision-replacement.md"
[ -f "$TMP/collision/audit/resolved/$AUDIT_NAME" ] || { echo "FAIL: collision record lost" >&2; exit 1; }
grep -q 'id: 20260101-120000-cafe' "$TMP/collision/audit/resolved/$AUDIT_NAME"
resolved_count="$(find "$TMP/collision/audit/resolved" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
[ "$resolved_count" = 2 ] || { echo "FAIL: expected both collision records" >&2; exit 1; }
[ ! -f "$TMP/collision/audit/$AUDIT_NAME" ] || { echo "FAIL: open audit remained after accept" >&2; exit 1; }
"$PY" "$ROOT/scripts/check-audit-compat.py" "$TMP/collision"

echo "=== crash after archive resumes idempotently ==="
mkdir -p "$TMP/crash"
cp -R "$FIX/." "$TMP/crash/"
make_replacement "$TMP/crash" "$TMP/crash-replacement.md"
if LLM_WIKI_TEST_CRASH_AFTER=archive \
  "$PY" "$ROOT/scripts/audit-resolve.py" "$TMP/crash" "$AUDIT_ID" \
    --outcome accept --summary "crash retry test" --replacement-file "$TMP/crash-replacement.md"; then
  echo "FAIL: crash injection unexpectedly succeeded" >&2
  exit 1
fi
[ ! -f "$TMP/crash/audit/$AUDIT_NAME" ] || { echo "FAIL: crash left stale open audit" >&2; exit 1; }
grep -q '知识库纠错应写入 audit' "$TMP/crash/wiki/entities/SampleConcept.md" || {
  echo "FAIL: target changed before state-first archive completed" >&2
  exit 1
}
"$PY" "$ROOT/scripts/audit-resolve.py" "$TMP/crash" "$AUDIT_ID" \
  --outcome accept --summary "crash retry test" --replacement-file "$TMP/crash-replacement.md"
"$PY" "$ROOT/scripts/audit-resolve.py" "$TMP/crash" "$AUDIT_ID" \
  --outcome accept --summary "crash retry test" --replacement-file "$TMP/crash-replacement.md"
grep -q '知识库纠错必须保留可恢复的 audit 记录' "$TMP/crash/wiki/entities/SampleConcept.md"
[ "$(grep -c "\[audit:$AUDIT_ID\]" "$TMP/crash/log.md")" = 1 ] || {
  echo "FAIL: retry duplicated log entry" >&2
  exit 1
}
"$PY" "$ROOT/scripts/check-audit-compat.py" "$TMP/crash"

echo "PASS: audit-resolve regression"
