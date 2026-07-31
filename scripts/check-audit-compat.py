#!/usr/bin/env python3
"""
check-audit-compat.py — 校验 wiki 内 open/resolved audit 是否符合契约 v1

用法：
  python scripts/check-audit-compat.py <wiki_root>
  python scripts/check-audit-compat.py <wiki_root> --smoke-write
  python scripts/check-audit-compat.py <wiki_root> --json

退出码：
  0 全部通过
  1 参数/路径错误或存在不合规 audit
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# 与 audit-review.py 保持同步（契约 v1）
REQUIRED_FIELDS = (
    "id",
    "target",
    "target_lines",
    "anchor_before",
    "anchor_after",
    "anchor_text",
    "severity",
    "author",
    "source",
    "created",
    "status",
)
VALID_SEVERITIES = {"error", "warn", "suggest", "info"}
VALID_SOURCES = {"manual", "agent", "obsidian-plugin", "web-viewer"}
VALID_STATUSES = {"open", "resolved"}
ID_RE = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

SCRIPT_DIR = Path(__file__).resolve().parent
AUDIT_FILE_PY = SCRIPT_DIR / "audit-file.py"
AUDIT_REVIEW_PY = SCRIPT_DIR / "audit-review.py"


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    result: dict = {}
    for line in m.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if val.startswith("[") and val.endswith("]"):
            items = []
            for p in val[1:-1].split(","):
                p = p.strip().strip('"').strip("'")
                if not p:
                    continue
                try:
                    items.append(int(p))
                except ValueError:
                    items.append(p)
            result[key] = items
        elif (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            result[key] = val[1:-1].replace("\\n", "\n").replace('\\"', '"')
        else:
            result[key] = val
    return result


def has_comment_body(text: str) -> bool:
    in_comment = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("# comment") or stripped.startswith("# 反馈"):
            in_comment = True
            continue
        if not in_comment:
            continue
        if stripped.startswith("#"):
            break
        if stripped and not stripped.startswith("<!--"):
            return True
    return False


def resolve_target(root: Path, target: str) -> Path | None:
    if not target:
        return None
    t = target.replace("\\", "/").lstrip("./")
    for c in (root / t, root / "wiki" / t):
        if c.is_file():
            return c
    return None


def validate_file(root: Path, path: Path, expect_status: str) -> list[str]:
    issues: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"read_error:{e}"]

    fm = parse_frontmatter(text)
    if fm is None:
        return ["no_frontmatter"]

    empty_ok = {"anchor_before", "anchor_after"}
    for field in REQUIRED_FIELDS:
        if field not in fm:
            issues.append(f"missing:{field}")
            continue
        if field in empty_ok:
            continue
        if fm[field] in ("", None, []):
            issues.append(f"empty:{field}")

    if fm.get("severity") not in VALID_SEVERITIES:
        issues.append(f"bad_severity:{fm.get('severity')}")
    if fm.get("source") not in VALID_SOURCES:
        issues.append(f"bad_source:{fm.get('source')}")
    status = fm.get("status")
    if status not in VALID_STATUSES:
        issues.append(f"bad_status:{status}")
    elif status != expect_status:
        issues.append(f"status_mismatch:want={expect_status},got={status}")

    lines = fm.get("target_lines")
    if not isinstance(lines, list) or len(lines) != 2:
        issues.append("bad_target_lines")
    else:
        try:
            a, b = int(lines[0]), int(lines[1])
            if a < 1 or b < a:
                issues.append("bad_target_lines_range")
        except (TypeError, ValueError):
            issues.append("bad_target_lines_type")

    aid = str(fm.get("id") or "")
    if aid and not ID_RE.match(aid):
        issues.append(f"bad_id_format:{aid}")

    target = str(fm.get("target") or "").replace("\\", "/")
    if target and "\\" in str(fm.get("target") or ""):
        issues.append("target_backslash")
    if target and resolve_target(root, target) is None:
        issues.append(f"target_missing:{target}")

    if not has_comment_body(text):
        issues.append("empty_comment")

    return issues


def collect_audits(root: Path) -> tuple[list[Path], list[Path]]:
    audit = root / "audit"
    open_files = sorted(p for p in audit.glob("*.md") if p.is_file()) if audit.is_dir() else []
    resolved_dir = audit / "resolved"
    resolved = (
        sorted(p for p in resolved_dir.glob("*.md") if p.is_file())
        if resolved_dir.is_dir()
        else []
    )
    return open_files, resolved


def check_wiki(root: Path) -> dict:
    open_files, resolved = collect_audits(root)
    report = {
        "wiki_root": str(root),
        "open_count": len(open_files),
        "resolved_count": len(resolved),
        "files": [],
        "ok": True,
    }
    if not open_files and not resolved:
        report["ok"] = False
        report["error"] = "no_audit_files"
        return report

    for path, expect in [(p, "open") for p in open_files] + [
        (p, "resolved") for p in resolved
    ]:
        issues = validate_file(root, path, expect)
        rel = str(path.relative_to(root)).replace("\\", "/")
        entry = {"path": rel, "expect_status": expect, "issues": issues}
        report["files"].append(entry)
        if issues:
            report["ok"] = False
    return report


def smoke_write(fixture_root: Path) -> dict:
    """Copy fixture to temp, write via audit-file.py --source obsidian-plugin, re-check."""
    if not AUDIT_FILE_PY.is_file():
        return {"ok": False, "error": f"missing {AUDIT_FILE_PY}"}

    with tempfile.TemporaryDirectory(prefix="audit-compat-") as tmp:
        dest = Path(tmp) / "wiki"
        shutil.copytree(fixture_root, dest)
        # remove gold open files so we only assert the new write? keep gold + add new
        cmd = [
            sys.executable,
            str(AUDIT_FILE_PY),
            str(dest),
            "--target",
            "wiki/entities/SampleConcept.md",
            "--anchor-text",
            "知识库纠错应写入 audit 目录而不是只留在聊天里。",
            "--comment",
            "V1 smoke: obsidian-plugin shape must match contract",
            "--severity",
            "suggest",
            "--author",
            "v1-smoke",
            "--source",
            "obsidian-plugin",
            "--anchor-before",
            "## 概述\n\n",
            "--anchor-after",
            "\n\n## 细节",
            "--target-lines",
            "11,11",
            "--slug",
            "v1-smoke-plugin",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        out = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0 or "SUCCESS:" not in out:
            return {
                "ok": False,
                "error": "audit-file_failed",
                "exit": proc.returncode,
                "output": out.strip(),
            }

        success_line = [ln for ln in out.splitlines() if ln.startswith("SUCCESS:")][-1]
        rel = success_line.split("SUCCESS:", 1)[1].strip()
        report = check_wiki(dest)
        # ensure the new file is among open and has source obsidian-plugin
        new_path = dest / rel.replace("/", "\\") if "\\" in rel else dest / Path(rel)
        if not new_path.is_file():
            # try posix
            new_path = dest / rel
        fm = parse_frontmatter(new_path.read_text(encoding="utf-8")) if new_path.is_file() else None
        plugin_ok = bool(fm and fm.get("source") == "obsidian-plugin")
        review = subprocess.run(
            [sys.executable, str(AUDIT_REVIEW_PY), str(dest), "--open"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return {
            "ok": report["ok"] and plugin_ok and review.returncode == 0,
            "written": rel,
            "source_ok": plugin_ok,
            "shape": report,
            "review_exit": review.returncode,
            "review_head": (review.stdout or "")[:500],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check audit files against contract v1")
    parser.add_argument("wiki_root", help="Knowledge base root")
    parser.add_argument(
        "--smoke-write",
        action="store_true",
        help="Copy wiki to temp and write one obsidian-plugin audit via audit-file.py",
    )
    parser.add_argument("--json", action="store_true", help="JSON report on stdout")
    args = parser.parse_args()

    root = Path(args.wiki_root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: wiki root not found: {root}", file=sys.stderr)
        return 1

    base = check_wiki(root)
    smoke = None
    if args.smoke_write:
        smoke = smoke_write(root)

    ok = base.get("ok") and (smoke is None or smoke.get("ok"))
    payload = {"check": base, "smoke_write": smoke, "ok": ok}

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"wiki: {root}")
        print(f"open: {base.get('open_count')}  resolved: {base.get('resolved_count')}")
        if base.get("error"):
            print(f"ERROR: {base['error']}")
        for f in base.get("files") or []:
            if f["issues"]:
                print(f"FAIL {f['path']}: {', '.join(f['issues'])}")
            else:
                print(f"OK   {f['path']}")
        if smoke is not None:
            print("--- smoke-write ---")
            if smoke.get("ok"):
                print(f"OK   wrote {smoke.get('written')} source=obsidian-plugin")
                print(f"OK   audit-review exit={smoke.get('review_exit')}")
            else:
                print(f"FAIL smoke: {json.dumps(smoke, ensure_ascii=False)[:800]}")
        print("PASS" if ok else "FAIL")

    return 0 if ok else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    sys.exit(main())
