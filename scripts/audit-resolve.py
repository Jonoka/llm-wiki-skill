#!/usr/bin/env python3
"""Resolve one audit without archive clobber or a post-edit stale-open window."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

from audit_contract import (
    ID_RE,
    normalize_relative_target,
    parse_frontmatter,
    resolve_vault_target,
    validate_frontmatter,
)


HASH_RE = re.compile(r"^- target_(before|after)_sha256: ([0-9a-f]{64})$", re.MULTILINE)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_audit(path: Path) -> tuple[str, dict, list[str]]:
    text = path.read_text(encoding="utf-8")
    frontmatter, parse_issues = parse_frontmatter(text)
    if frontmatter is None:
        raise ValueError(", ".join(parse_issues))
    return text, frontmatter, parse_issues


def find_audit(root: Path, reference: str) -> Path | None:
    audit_dir = root / "audit"
    resolved_dir = audit_dir / "resolved"
    if ID_RE.fullmatch(reference):
        candidates = list(audit_dir.glob("*.md")) + list(resolved_dir.glob("*.md"))
        for candidate in candidates:
            try:
                _, frontmatter, _ = read_audit(candidate)
            except (OSError, ValueError):
                continue
            if frontmatter.get("id") == reference:
                return candidate
        return None

    try:
        rel = normalize_relative_target(reference)
    except ValueError:
        return None
    if not rel.startswith("audit/") or not rel.endswith(".md"):
        return None
    parts = rel.split("/")
    if len(parts) not in (2, 3) or (len(parts) == 3 and parts[1] != "resolved"):
        return None
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if candidate.is_file():
        return candidate
    if len(parts) == 2:
        resolved = resolved_dir / parts[-1]
        if resolved.is_file():
            return resolved
    return None


def find_resolved_by_id(resolved_dir: Path, audit_id: str) -> Path | None:
    for candidate in resolved_dir.glob("*.md"):
        try:
            _, frontmatter, _ = read_audit(candidate)
        except (OSError, ValueError):
            continue
        if frontmatter.get("id") == audit_id:
            return candidate
    return None


def resolution_body(
    text: str,
    outcome: str,
    summary: str,
    before_hash: str | None,
    after_hash: str | None,
) -> str:
    updated, count = re.subn(r"(?m)^status: open$", "status: resolved", text, count=1)
    if count != 1:
        raise ValueError("open audit has no exact 'status: open' line")
    lines = ["# Resolution", "", f"- outcome: {outcome}", f"- summary: {summary}"]
    if before_hash and after_hash:
        lines.extend(
            [
                f"- target_before_sha256: {before_hash}",
                f"- target_after_sha256: {after_hash}",
            ]
        )
    resolution = "\n".join(lines) + "\n"
    if re.search(r"(?m)^# Resolution\s*$", updated):
        return re.sub(r"(?ms)^# Resolution\s*\n.*\Z", resolution, updated)
    return updated.rstrip() + "\n\n" + resolution


def archive_no_clobber(
    source: Path,
    resolved_dir: Path,
    audit_id: str,
    body: str,
) -> Path:
    existing = find_resolved_by_id(resolved_dir, audit_id)
    if existing is not None and existing.read_text(encoding="utf-8") == body:
        source.unlink()
        return existing

    preferred = resolved_dir / source.name
    candidates = [preferred, resolved_dir / f"{source.stem}-{audit_id}{source.suffix}"]
    for index in range(2, 1000):
        candidates.append(resolved_dir / f"{source.stem}-{audit_id}-{index}{source.suffix}")
    for destination in candidates:
        try:
            with destination.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError:
            continue
        source.unlink()
        return destination
    raise OSError("could not allocate a no-clobber resolved filename")


def atomic_write_text(path: Path, text: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.audit-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def append_log_once(root: Path, audit_id: str, summary: str) -> None:
    log_path = root / "log.md"
    marker = f"[audit:{audit_id}]"
    existing = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    if marker in existing:
        return
    separator = "" if not existing or existing.endswith("\n") else "\n"
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            f"{separator}\n## {date.today().isoformat()} audit | resolved {audit_id} — {summary} {marker}\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wiki_root")
    parser.add_argument("audit", help="audit id or vault-relative audit/*.md path")
    parser.add_argument("--outcome", choices=("accept", "partial", "reject", "archive"), required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument(
        "--replacement-file",
        help="UTF-8 full target contents; required for accept/partial and avoids Windows CLI size limits",
    )
    args = parser.parse_args()

    root = Path(args.wiki_root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: wiki root not found: {root}", file=sys.stderr)
        return 1
    audit_path = find_audit(root, args.audit)
    if audit_path is None:
        print(f"ERROR: audit not found or unsafe reference: {args.audit}", file=sys.stderr)
        return 1

    summary = " ".join(args.summary.split())
    if not summary:
        print("ERROR: --summary must not be empty", file=sys.stderr)
        return 1
    needs_replacement = args.outcome in ("accept", "partial")
    if needs_replacement != bool(args.replacement_file):
        print("ERROR: accept/partial require --replacement-file; reject/archive must not use it", file=sys.stderr)
        return 1

    try:
        text, frontmatter, parse_issues = read_audit(audit_path)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: invalid audit: {error}", file=sys.stderr)
        return 1
    expect_status = "resolved" if audit_path.parent.name == "resolved" else "open"
    issues = validate_frontmatter(root, frontmatter, parse_issues, expect_status=expect_status)
    if issues:
        print(f"ERROR: invalid audit: {', '.join(issues)}", file=sys.stderr)
        return 1

    audit_id = str(frontmatter["id"])
    target = resolve_vault_target(root, str(frontmatter["target"]))
    if target is None:
        print("ERROR: audit target is missing or outside the wiki root", file=sys.stderr)
        return 1

    replacement = None
    before_hash = after_hash = None
    if needs_replacement:
        try:
            replacement = Path(args.replacement_file).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            print(f"ERROR: cannot read replacement: {error}", file=sys.stderr)
            return 1
        after_hash = sha256_text(replacement)

    resolved_dir = root / "audit" / "resolved"
    resolved_dir.mkdir(parents=True, exist_ok=True)
    if expect_status == "open":
        if needs_replacement:
            before_hash = sha256_text(target.read_text(encoding="utf-8"))
        try:
            body = resolution_body(text, args.outcome, summary, before_hash, after_hash)
            audit_path = archive_no_clobber(audit_path, resolved_dir, audit_id, body)
        except (OSError, ValueError) as error:
            print(f"ERROR: cannot archive audit: {error}", file=sys.stderr)
            return 1
    elif needs_replacement:
        hashes = dict(HASH_RE.findall(text))
        before_hash, recorded_after = hashes.get("before"), hashes.get("after")
        if not before_hash or recorded_after != after_hash:
            print("ERROR: replacement does not match the archived resolution", file=sys.stderr)
            return 1

    print(f"ARCHIVED:{audit_path.relative_to(root).as_posix()}")
    if os.environ.get("LLM_WIKI_TEST_CRASH_AFTER") == "archive":
        return 86

    if needs_replacement and replacement is not None:
        current_hash = sha256_text(target.read_text(encoding="utf-8"))
        if current_hash == before_hash:
            atomic_write_text(target, replacement)
        elif current_hash != after_hash:
            print("ERROR: target changed after the audit was archived; refusing to clobber", file=sys.stderr)
            return 1
        if os.environ.get("LLM_WIKI_TEST_CRASH_AFTER") == "target":
            return 87

    append_log_once(root, audit_id, summary)
    print(f"SUCCESS:{audit_path.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
