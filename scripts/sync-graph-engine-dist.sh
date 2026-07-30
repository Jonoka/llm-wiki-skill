#!/bin/bash
# sync-graph-engine-dist.sh — copy prebuilt engine.iife.js into skill-assets for default install
#
# Usage:
#   npm run build -w @llm-wiki/graph-engine
#   bash scripts/sync-graph-engine-dist.sh
#
# Exit: 0 ok; 1 missing build output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$ROOT/packages/graph-engine/dist/engine.iife.js"
DEST_DIR="$ROOT/skill-assets/graph-engine/dist"
DEST="$DEST_DIR/engine.iife.js"
INFO="$DEST_DIR/BUILD-INFO.txt"

if [ ! -f "$SRC" ]; then
  echo "ERROR: missing $SRC" >&2
  echo "       Run: npm run build -w @llm-wiki/graph-engine" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# Strip sourceMappingURL so offline HTML does not look for missing .map next to IIFE.
if command -v perl >/dev/null 2>&1; then
  perl -pe 's|//# sourceMappingURL=.*$||' "$SRC" > "$DEST"
else
  cp "$SRC" "$DEST"
fi

if command -v sha256sum >/dev/null 2>&1; then
  HASH="$(sha256sum "$DEST" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
  HASH="$(shasum -a 256 "$DEST" | awk '{print $1}')"
else
  HASH="unknown"
fi

BYTES="$(wc -c < "$DEST" | tr -d ' ')"
STAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat > "$INFO" <<EOF
source=packages/graph-engine
artifact=engine.iife.js
built_for=skill default install (Jonoka)
sha256=$HASH
bytes=$BYTES
synced_at=$STAMP
note=Rebuild with: npm run build -w @llm-wiki/graph-engine && bash scripts/sync-graph-engine-dist.sh
EOF

echo "Synced graph-engine IIFE -> $DEST"
echo "  bytes=$BYTES"
echo "  sha256=$HASH"
