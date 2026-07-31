#!/bin/bash
# sync-graph-engine-dist.sh — copy prebuilt engine.iife.js into skill-assets for default install
#
# Usage:
#   npm run build -w @llm-wiki/graph-engine
#   bash scripts/sync-graph-engine-dist.sh          # write skill-assets
#   bash scripts/sync-graph-engine-dist.sh --check  # fail if skill-assets drifted
#
# Exit: 0 ok; 1 missing build / drift / bad args

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$ROOT/packages/graph-engine/dist/engine.iife.js"
DEST_DIR="$ROOT/skill-assets/graph-engine/dist"
DEST="$DEST_DIR/engine.iife.js"
INFO="$DEST_DIR/BUILD-INFO.txt"

MODE="sync"
case "${1:-}" in
  "" ) MODE="sync" ;;
  --check | check ) MODE="check" ;;
  -h | --help )
    sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  * )
    echo "ERROR: unknown arg: $1 (use --check or no args)" >&2
    exit 1
    ;;
esac

# Normalize like workbench/scripts/check-skill-assets-graph-engine.mjs:
# CRLF→LF, strip sourceMappingURL, trim trailing whitespace, single trailing newline.
hash_file_normalized() {
  local path="$1"
  local tmp hash
  tmp="$(mktemp "${TMPDIR:-/tmp}/llm-wiki-iife-hash.XXXXXX")"
  if command -v perl >/dev/null 2>&1; then
    # Match Node: strip map URL, trim trailing whitespace, force single trailing \n
    perl -0777 -pe 's/\r\n/\n/g; s/\r/\n/g; s|//# sourceMappingURL=.*$||m; s/\s+\z//; $_ .= "\n"' "$path" > "$tmp"
  else
    tr -d '\r' < "$path" | sed 's|//# sourceMappingURL=.*||' > "$tmp"
    # trim trailing blank lines / spaces roughly, then force one trailing newline
    if command -v python3 >/dev/null 2>&1; then
      python3 -c 'import pathlib,sys; p=pathlib.Path(sys.argv[1]); t=p.read_text(encoding="utf-8"); p.write_text(t.rstrip()+"\n", encoding="utf-8")' "$tmp"
    else
      printf '\n' >> "$tmp"
    fi
  fi
  if command -v sha256sum >/dev/null 2>&1; then
    hash="$(sha256sum "$tmp" | awk '{print $1}')"
  elif command -v shasum >/dev/null 2>&1; then
    hash="$(shasum -a 256 "$tmp" | awk '{print $1}')"
  else
    rm -f "$tmp"
    echo "ERROR: need sha256sum or shasum" >&2
    exit 1
  fi
  rm -f "$tmp"
  printf '%s\n' "$hash"
}

if [ ! -f "$SRC" ]; then
  echo "ERROR: missing $SRC" >&2
  echo "       Run: npm run build -w @llm-wiki/graph-engine" >&2
  exit 1
fi

if [ "$MODE" = "check" ]; then
  if [ ! -f "$DEST" ]; then
    echo "ERROR: missing skill-assets IIFE: $DEST" >&2
    echo "       Run: npm run build -w @llm-wiki/graph-engine && bash scripts/sync-graph-engine-dist.sh" >&2
    exit 1
  fi
  SRC_HASH="$(hash_file_normalized "$SRC")"
  DEST_HASH="$(hash_file_normalized "$DEST")"
  if [ "$SRC_HASH" != "$DEST_HASH" ]; then
    echo "ERROR: skill-assets graph-engine IIFE is out of date (dist drift)" >&2
    echo "       packages/graph-engine/dist  sha256=$SRC_HASH" >&2
    echo "       skill-assets/.../engine.iife.js sha256=$DEST_HASH" >&2
    echo "       Fix: npm run build -w @llm-wiki/graph-engine && bash scripts/sync-graph-engine-dist.sh" >&2
    echo "       Then commit skill-assets/graph-engine/dist/" >&2
    exit 1
  fi
  if [ -f "$INFO" ]; then
    INFO_HASH="$(grep -E '^sha256=' "$INFO" | head -1 | cut -d= -f2- || true)"
    if [ -n "$INFO_HASH" ] && [ "$INFO_HASH" != "$DEST_HASH" ]; then
      echo "ERROR: BUILD-INFO.txt sha256 does not match skill-assets IIFE" >&2
      echo "       BUILD-INFO sha256=$INFO_HASH" >&2
      echo "       file      sha256=$DEST_HASH" >&2
      echo "       Fix: bash scripts/sync-graph-engine-dist.sh" >&2
      exit 1
    fi
  fi
  echo "OK: skill-assets graph-engine IIFE matches packages build (sha256=$DEST_HASH)"
  exit 0
fi

mkdir -p "$DEST_DIR"

# Strip sourceMappingURL so offline HTML does not look for missing .map next to IIFE.
if command -v perl >/dev/null 2>&1; then
  perl -pe 's|//# sourceMappingURL=.*$||' "$SRC" > "$DEST"
else
  cp "$SRC" "$DEST"
fi

# BUILD-INFO sha256 uses the same normalization as --check / Node gate.
HASH="$(hash_file_normalized "$DEST")"
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
