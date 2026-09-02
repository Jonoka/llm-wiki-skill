"""Shared audit v1 parsing and vault-containment rules."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path, PureWindowsPath


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
VALID_SEVERITIES = {"error", "warn", "suggest", "info"}
VALID_SOURCES = {"manual", "agent", "obsidian-plugin", "web-viewer"}
VALID_STATUSES = {"open", "resolved"}
ID_RE = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")
CREATED_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def normalize_relative_target(target: str) -> str:
    """Return a canonical vault-relative spelling or raise ValueError."""
    raw = str(target or "")
    normalized = raw.replace("\\", "/")
    if (
        not normalized
        or normalized.startswith("/")
        or PureWindowsPath(raw).drive
        or "\x00" in normalized
    ):
        raise ValueError("target must be relative to the wiki root")
    parts = normalized.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("target must not contain empty or dot path segments")
    return "/".join(parts)


def is_wiki_markdown_target(target: str) -> bool:
    try:
        normalized = normalize_relative_target(target)
    except ValueError:
        return False
    return normalized == target and normalized.startswith("wiki/") and normalized.lower().endswith(".md")


def resolve_vault_target(root: Path, target: str, *, allow_aliases: bool = False) -> Path | None:
    """Resolve a Markdown target and reject absolute, traversal, and escaping symlinks."""
    try:
        rel = normalize_relative_target(target)
    except ValueError:
        return None

    candidates = [rel]
    if allow_aliases:
        if not rel.lower().endswith(".md"):
            candidates.append(f"{rel}.md")
        if not rel.startswith("wiki/"):
            candidates.append(f"wiki/{rel}")
            if not rel.lower().endswith(".md"):
                candidates.append(f"wiki/{rel}.md")
        if "/" not in rel and rel.lower().endswith(".md"):
            candidates.extend(
                f"wiki/{sub}/{rel}"
                for sub in ("entities", "topics", "sources", "comparisons", "synthesis", "queries")
            )

    root_resolved = root.resolve()
    for candidate in dict.fromkeys(candidates):
        path = (root_resolved / candidate).resolve()
        try:
            path.relative_to(root_resolved)
        except ValueError:
            continue
        if path.is_file():
            return path
    return None


def parse_frontmatter(text: str) -> tuple[dict | None, list[str]]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, ["no_frontmatter"]
    result: dict = {}
    issues: list[str] = []
    for line_number, line in enumerate(match.group(1).split("\n"), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            issues.append(f"bad_frontmatter_line:{line_number}")
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        if not key:
            issues.append(f"bad_frontmatter_line:{line_number}")
            continue
        if key in result:
            issues.append(f"duplicate:{key}")
            continue
        val = rest.strip()
        if val.startswith("[") and val.endswith("]"):
            items = []
            for part in val[1:-1].split(","):
                part = part.strip().strip('"').strip("'")
                if not part:
                    continue
                try:
                    items.append(int(part))
                except ValueError:
                    items.append(part)
            result[key] = items
        elif (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            result[key] = val[1:-1].replace("\\n", "\n").replace('\\"', '"')
        else:
            result[key] = val
    return result, issues


def _valid_created(value: object) -> bool:
    text = str(value or "")
    if not CREATED_RE.fullmatch(text):
        return False
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_frontmatter(
    root: Path,
    frontmatter: dict,
    parse_issues: list[str] | None = None,
    *,
    expect_status: str | None = None,
) -> list[str]:
    issues = list(parse_issues or [])
    keys = set(frontmatter)
    required = set(REQUIRED_FIELDS)
    issues.extend(f"missing:{field}" for field in REQUIRED_FIELDS if field not in keys)
    issues.extend(f"extra:{field}" for field in sorted(keys - required))

    for field in required - {"anchor_before", "anchor_after"}:
        if field in frontmatter and frontmatter[field] in ("", None, []):
            issues.append(f"empty:{field}")

    if frontmatter.get("severity") not in VALID_SEVERITIES:
        issues.append(f"bad_severity:{frontmatter.get('severity')}")
    if frontmatter.get("source") not in VALID_SOURCES:
        issues.append(f"bad_source:{frontmatter.get('source')}")
    status = frontmatter.get("status")
    if status not in VALID_STATUSES:
        issues.append(f"bad_status:{status}")
    elif expect_status and status != expect_status:
        issues.append(f"status_mismatch:want={expect_status},got={status}")

    lines = frontmatter.get("target_lines")
    if not isinstance(lines, list) or len(lines) != 2:
        issues.append("bad_target_lines")
    elif not all(isinstance(value, int) for value in lines):
        issues.append("bad_target_lines_type")
    elif lines[0] < 1 or lines[1] < lines[0]:
        issues.append("bad_target_lines_range")

    audit_id = str(frontmatter.get("id") or "")
    if audit_id and not ID_RE.fullmatch(audit_id):
        issues.append(f"bad_id_format:{audit_id}")
    if not _valid_created(frontmatter.get("created")):
        issues.append(f"bad_created:{frontmatter.get('created')}")

    raw_target = str(frontmatter.get("target") or "")
    try:
        target = normalize_relative_target(raw_target)
    except ValueError:
        issues.append(f"target_invalid:{raw_target}")
    else:
        if raw_target != target:
            issues.append("target_not_canonical")
        if not is_wiki_markdown_target(target):
            issues.append(f"target_not_wiki_page:{target}")
        elif resolve_vault_target(root, target) is None:
            issues.append(f"target_missing:{target}")

    return issues
