#!/usr/bin/env python3
"""
audit-review.py — 列出并按 target 分组 audit 反馈（sdyckjq 路径约定）

用法：
    python audit-review.py <wiki-root> [--open|--resolved|--all] [--json]

示例：
    python scripts/audit-review.py ~/Documents/我的知识库 --open
    python scripts/audit-review.py . --all --json

读取 <wiki-root>/audit/*.md（open）与 audit/resolved/*.md（resolved），
解析 YAML frontmatter，按 target 分组输出。供 audit 工作流开局使用。

退出码：
  0 — 完成
  1 — 参数错误或 wiki 根无效
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

REQUIRED_FIELDS = (
    "id",
    "target",
    "target_lines",
    "anchor_before",
    "anchor_text",
    "anchor_after",
    "severity",
    "author",
    "source",
    "created",
    "status",
)

SEVERITY_ORDER = {"error": 0, "warn": 1, "suggest": 2, "info": 3}
VALID_SEVERITIES = set(SEVERITY_ORDER)
VALID_SOURCES = {"obsidian-plugin", "web-viewer", "manual", "agent"}
VALID_STATUSES = {"open", "resolved"}


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    body = m.group(1)
    result: dict = {}
    for line in body.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = []
            for p in inner.split(","):
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


def extract_comment_one_line(text: str) -> str:
    in_comment = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("# comment") or stripped.startswith("# 反馈"):
            in_comment = True
            continue
        if not in_comment:
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            break
        return stripped[:120]
    return "(无正文)"


def validate_shape(fm: dict) -> list[str]:
    issues: list[str] = []
    # anchor_before / anchor_after may be empty strings (selection at file edge)
    empty_ok = {"anchor_before", "anchor_after"}
    for field in REQUIRED_FIELDS:
        if field not in fm:
            issues.append(f"missing:{field}")
            continue
        if field in empty_ok:
            continue
        if fm[field] in ("", None, []):
            issues.append(f"missing:{field}")
    sev = fm.get("severity")
    if sev and sev not in VALID_SEVERITIES:
        issues.append(f"bad_severity:{sev}")
    src = fm.get("source")
    if src and src not in VALID_SOURCES:
        issues.append(f"bad_source:{src}")
    status = fm.get("status")
    if status and status not in VALID_STATUSES:
        issues.append(f"bad_status:{status}")
    lines = fm.get("target_lines")
    if lines is not None:
        if not isinstance(lines, list) or len(lines) != 2:
            issues.append("bad_target_lines")
    return issues


def resolve_target_path(root: Path, target: str) -> Path | None:
    """Resolve target relative to wiki root. Accept wiki/... or bare paths."""
    if not target:
        return None
    t = target.replace("\\", "/").lstrip("./")
    candidates = [
        root / t,
        root / "wiki" / t,
    ]
    # bare filename: search under wiki/
    if "/" not in t and not t.endswith(".md"):
        candidates.append(root / "wiki" / f"{t}.md")
    if "/" not in t and t.endswith(".md"):
        for sub in ("entities", "topics", "sources", "comparisons", "synthesis", "queries"):
            candidates.append(root / "wiki" / sub / t)
    for c in candidates:
        if c.is_file():
            return c
    return None


def collect_files(audit_dir: Path, mode: str) -> list[Path]:
    files: list[Path] = []
    if mode in ("open", "all"):
        files.extend(sorted(p for p in audit_dir.glob("*.md") if p.name != ".gitkeep"))
    if mode in ("resolved", "all"):
        resolved = audit_dir / "resolved"
        if resolved.is_dir():
            files.extend(
                sorted(p for p in resolved.glob("*.md") if p.name != ".gitkeep")
            )
    return files


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1 if len(argv) < 2 else 0

    root = Path(argv[1]).expanduser().resolve()
    mode = "open"
    as_json = False
    for arg in argv[2:]:
        if arg == "--open":
            mode = "open"
        elif arg == "--resolved":
            mode = "resolved"
        elif arg == "--all":
            mode = "all"
        elif arg == "--json":
            as_json = True
        else:
            print(f"Unknown flag: {arg}", file=sys.stderr)
            return 1

    if not root.is_dir():
        print(f"ERROR: wiki root not found: {root}", file=sys.stderr)
        return 1
    if not (root / ".wiki-schema.md").is_file() and not (root / "wiki").is_dir():
        print(
            f"ERROR: not a wiki root (missing .wiki-schema.md and wiki/): {root}",
            file=sys.stderr,
        )
        return 1

    audit_dir = root / "audit"
    if not audit_dir.is_dir():
        if as_json:
            print(json.dumps({"mode": mode, "total": 0, "targets": {}, "note": "no_audit_dir"}))
        else:
            print(f"No audit/ directory at {audit_dir} (0 {mode} audits).")
            print("Tip: init creates audit/; or mkdir -p audit/resolved")
        return 0

    files = collect_files(audit_dir, mode)
    if not files:
        if as_json:
            print(json.dumps({"mode": mode, "total": 0, "targets": {}}))
        else:
            print(f"No {mode} audit files found.")
        return 0

    grouped: dict[str, list[dict]] = defaultdict(list)
    shape_errors: list[dict] = []

    for p in files:
        text = p.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            shape_errors.append({"path": str(p.relative_to(root)), "issues": ["missing_frontmatter"]})
            continue
        issues = validate_shape(fm)
        rel = str(p.relative_to(root)).replace("\\", "/")
        target = str(fm.get("target", "(no-target)"))
        target_path = resolve_target_path(root, target) if target != "(no-target)" else None
        if target != "(no-target)" and target_path is None:
            issues.append("target_missing")

        entry = {
            **fm,
            "_path": rel,
            "_one_liner": extract_comment_one_line(text),
            "_target_exists": target_path is not None,
            "_shape_issues": issues,
        }
        if issues:
            shape_errors.append({"path": rel, "issues": issues})
        grouped[target].append(entry)

    total = sum(len(v) for v in grouped.values())

    if as_json:
        out = {
            "mode": mode,
            "total": total,
            "targets": {
                t: [
                    {
                        "id": e.get("id"),
                        "severity": e.get("severity"),
                        "status": e.get("status"),
                        "author": e.get("author"),
                        "source": e.get("source"),
                        "created": e.get("created"),
                        "path": e.get("_path"),
                        "one_liner": e.get("_one_liner"),
                        "target_exists": e.get("_target_exists"),
                        "shape_issues": e.get("_shape_issues"),
                    }
                    for e in sorted(
                        entries,
                        key=lambda x: (
                            SEVERITY_ORDER.get(str(x.get("severity", "info")), 99),
                            str(x.get("created", "")),
                        ),
                    )
                ]
                for t, entries in sorted(grouped.items())
            },
            "shape_errors": shape_errors,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    print(f"{mode.upper()} audits: {total} across {len(grouped)} target file(s)\n")

    for target in sorted(grouped.keys()):
        entries = grouped[target]
        entries.sort(
            key=lambda e: (
                SEVERITY_ORDER.get(str(e.get("severity", "info")), 99),
                str(e.get("created", "")),
            )
        )
        exists_mark = "✓" if entries[0].get("_target_exists") else "✗ missing"
        print(f"{target}  ({len(entries)} {mode})  [{exists_mark}]")
        for e in entries:
            sev = e.get("severity", "?")
            aid = e.get("id", "?")
            author = e.get("author", "?")
            created = str(e.get("created", "?"))[:10]
            line = e.get("_one_liner", "")
            issues = e.get("_shape_issues") or []
            extra = f"  ⚠ {','.join(issues)}" if issues else ""
            print(f"   [{aid}] {sev}: {line}  —  {author}, {created}{extra}")
        print()

    if shape_errors:
        print(f"Shape/target issues: {len(shape_errors)} file(s)")
        for err in shape_errors:
            print(f"  - {err['path']}: {', '.join(err['issues'])}")

    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    sys.exit(main(sys.argv))
