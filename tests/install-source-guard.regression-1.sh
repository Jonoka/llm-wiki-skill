#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="${TMPDIR:-/tmp}/llm-wiki-install-guard-$$"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

before="$(sha256sum "$ROOT/SKILL.md" | awk '{print $1}')"
if (cd "$ROOT" && bash install.sh --platform codex --target-dir .) >"$TMP-self.log" 2>&1; then
  echo "FAIL: installer accepted its source tree as target" >&2
  exit 1
fi
after="$(sha256sum "$ROOT/SKILL.md" | awk '{print $1}')"
[ "$before" = "$after" ] || { echo "FAIL: self-install modified source SKILL.md" >&2; exit 1; }
grep -q '拒绝' "$TMP-self.log" || { echo "FAIL: self-install refusal was not explicit" >&2; exit 1; }

if bash "$ROOT/install.sh" --platform codex --target-dir "$ROOT/scripts/unsafe-install" \
  >"$TMP-child.log" 2>&1; then
  echo "FAIL: installer accepted a target inside its source tree" >&2
  exit 1
fi
[ ! -e "$ROOT/scripts/unsafe-install" ] || { echo "FAIL: unsafe child target was created" >&2; exit 1; }

mkdir -p "$TMP/target"
printf 'preserve me\n' > "$TMP/target/local-note.txt"
bash "$ROOT/install.sh" --platform codex --target-dir "$TMP/target" >/dev/null
[ -f "$TMP/target/SKILL.md" ] || { echo "FAIL: staged install omitted SKILL.md" >&2; exit 1; }
[ -f "$TMP/target/local-note.txt" ] || { echo "FAIL: staged install dropped unmanaged file" >&2; exit 1; }
if find "$TMP" -maxdepth 1 \( -name '.llm-wiki-stage.*' -o -name '.llm-wiki-backup.*' \) | grep -q .; then
  echo "FAIL: staged install left temporary directories" >&2
  exit 1
fi

echo "PASS: install source guard regression"
