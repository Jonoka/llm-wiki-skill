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
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from audit_contract import parse_frontmatter, validate_frontmatter

SCRIPT_DIR = Path(__file__).resolve().parent
AUDIT_FILE_PY = SCRIPT_DIR / "audit-file.py"
AUDIT_REVIEW_PY = SCRIPT_DIR / "audit-review.py"


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


def validate_file(root: Path, path: Path, expect_status: str) -> list[str]:
    issues: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"read_error:{e}"]

    fm, parse_issues = parse_frontmatter(text)
    if fm is None:
        return parse_issues

    issues.extend(validate_frontmatter(root, fm, parse_issues, expect_status=expect_status))

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
        fm = parse_frontmatter(new_path.read_text(encoding="utf-8"))[0] if new_path.is_file() else None
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
