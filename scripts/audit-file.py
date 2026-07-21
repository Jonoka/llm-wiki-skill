#!/usr/bin/env python3
"""
audit-file.py — 写入一条 open audit（Phase 1 手动/agent 入口）

用法：
    python audit-file.py <wiki-root> \\
        --target wiki/entities/Foo.md \\
        --anchor-text "原文片段" \\
        --comment "这里的数字有误" \\
        [--severity warn] \\
        [--anchor-before "..."] \\
        [--anchor-after "..."] \\
        [--target-lines 10,15] \\
        [--author you] \\
        [--source manual|agent] \\
        [--slug short-hint]

成功时打印：SUCCESS:<relative-path>
"""

from __future__ import annotations

import argparse
import re
import secrets
import sys
from datetime import datetime
from pathlib import Path


def slugify(text: str, max_len: int = 40) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", text, flags=re.UNICODE)
    text = text.strip("-") or "note"
    return text[:max_len]


def yaml_escape(s: str) -> str:
    """Quote a string for YAML double-quoted scalar."""
    return (
        '"'
        + s.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "")
        + '"'
    )


def resolve_target(root: Path, target: str) -> Path | None:
    t = target.replace("\\", "/").lstrip("./")
    candidates = [root / t, root / "wiki" / t]
    if not t.endswith(".md"):
        candidates.append(root / f"{t}.md")
        candidates.append(root / "wiki" / f"{t}.md")
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None


def normalize_target(root: Path, target_path: Path) -> str:
    try:
        rel = target_path.relative_to(root.resolve())
    except ValueError:
        rel = target_path
    return str(rel).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an open audit feedback file")
    parser.add_argument("wiki_root", help="Knowledge base root")
    parser.add_argument("--target", required=True, help="Path relative to wiki root, e.g. wiki/entities/Foo.md")
    parser.add_argument("--anchor-text", required=True, help="Exact selected text")
    parser.add_argument("--comment", required=True, help="Human feedback body")
    parser.add_argument(
        "--severity",
        default="warn",
        choices=["info", "suggest", "warn", "error"],
    )
    parser.add_argument("--anchor-before", default="", help="Up to ~80 chars before selection")
    parser.add_argument("--anchor-after", default="", help="Up to ~80 chars after selection")
    parser.add_argument(
        "--target-lines",
        default="1,1",
        help="1-indexed inclusive range, e.g. 10,15",
    )
    parser.add_argument("--author", default="user")
    parser.add_argument(
        "--source",
        default="manual",
        choices=["manual", "agent", "obsidian-plugin", "web-viewer"],
    )
    parser.add_argument("--slug", default="", help="Filename slug hint")
    args = parser.parse_args()

    root = Path(args.wiki_root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: wiki root not found: {root}", file=sys.stderr)
        return 1

    target_path = resolve_target(root, args.target)
    if target_path is None:
        print(f"ERROR: target not found: {args.target}", file=sys.stderr)
        return 1

    target_rel = normalize_target(root, target_path)

    try:
        start_s, end_s = [p.strip() for p in args.target_lines.split(",", 1)]
        start_line, end_line = int(start_s), int(end_s)
    except Exception:
        print("ERROR: --target-lines must be like 10,15", file=sys.stderr)
        return 1

    now = datetime.now().astimezone()
    stamp = now.strftime("%Y%m%d-%H%M%S")
    hex4 = secrets.token_hex(2)
    audit_id = f"{stamp}-{hex4}"
    slug = slugify(args.slug or args.comment or args.anchor_text)
    filename = f"{stamp}-{slug}.md"

    audit_dir = root / "audit"
    resolved_dir = audit_dir / "resolved"
    audit_dir.mkdir(parents=True, exist_ok=True)
    resolved_dir.mkdir(parents=True, exist_ok=True)

    out_path = audit_dir / filename
    if out_path.exists():
        filename = f"{stamp}-{slug}-{hex4}.md"
        out_path = audit_dir / filename
        audit_id = f"{stamp}-{hex4}"

    created = now.isoformat(timespec="seconds")

    body = f"""---
id: {audit_id}
target: {target_rel}
target_lines: [{start_line}, {end_line}]
anchor_before: {yaml_escape(args.anchor_before[:200])}
anchor_text: {yaml_escape(args.anchor_text)}
anchor_after: {yaml_escape(args.anchor_after[:200])}
severity: {args.severity}
author: {args.author}
source: {args.source}
created: {created}
status: open
---

# Comment

{args.comment.strip()}

# Resolution

<!-- Filled when processed and moved to audit/resolved/ -->
"""

    out_path.write_text(body, encoding="utf-8")
    rel = str(out_path.relative_to(root)).replace("\\", "/")
    print(f"SUCCESS:{rel}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    sys.exit(main())
