#!/usr/bin/env python3
"""Zephyr's deterministic, local-only vault maintenance commands.

This module deliberately never invokes an agent CLI or an LLM API. Agents may
prepare proposals, but people use ``activate`` and ``archive`` to apply the
resulting lifecycle changes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by installation docs
    raise SystemExit("PyYAML is required. Run: python -m pip install -r requirements.txt") from exc


VAULT_DIR = Path(__file__).resolve().parent.parent
CAPTURE_DIR = VAULT_DIR / "Capture"
ACTIVE_DIR = VAULT_DIR / "Active"
BRAIN_DIR = VAULT_DIR / "Brain"
ARCHIVE_DIR = VAULT_DIR / "Archive"
SYSTEM_DIR = VAULT_DIR / "System"
INDEX_PATH = SYSTEM_DIR / "index.json"
STATUS_PATH = SYSTEM_DIR / "status.json"
REVIEW_QUEUE_PATH = SYSTEM_DIR / "review-queue.json"
CONTENT_DIRS = (CAPTURE_DIR, ACTIVE_DIR, BRAIN_DIR, ARCHIVE_DIR)
INVALID_FILENAME = re.compile(r'[\\/:*?"<>|]')
WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


class FrontmatterError(ValueError):
    """A note has an absent, malformed, or non-mapping frontmatter block."""


class CommandError(ValueError):
    """A requested lifecycle operation is not safe to perform."""


def ensure_roots() -> None:
    """Create Zephyr-owned empty roots; never relocate content implicitly."""
    for directory in (*CONTENT_DIRS, SYSTEM_DIR):
        Path(directory).mkdir(parents=True, exist_ok=True)


def _frontmatter_bounds(content: str) -> tuple[int, int] | None:
    if not content.startswith("---"):
        return None
    first_line_end = content.find("\n")
    if first_line_end < 0 or content[:first_line_end].strip() != "---":
        return None
    match = re.search(r"(?m)^---\s*$", content[first_line_end + 1 :])
    if not match:
        raise FrontmatterError("frontmatter begins with --- but has no closing ---")
    start = first_line_end + 1
    end = start + match.start()
    body_start = start + match.end()
    if body_start < len(content) and content[body_start] == "\n":
        body_start += 1
    return start, end, body_start


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse standard YAML frontmatter without modifying the Markdown body."""
    bounds = _frontmatter_bounds(content)
    if bounds is None:
        return {}, content
    start, end, body_start = bounds
    try:
        data = yaml.safe_load(content[start:end])
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"invalid YAML frontmatter: {exc.problem or exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter must be a YAML mapping")
    return data, content[body_start:]


def _safe_json(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _safe_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_safe_json(item) for item in value]
    return value


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def load_index() -> dict[str, Any]:
    try:
        with INDEX_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_index(index: dict[str, Any]) -> None:
    _atomic_write(INDEX_PATH, json.dumps(_safe_json(index), indent=2, ensure_ascii=False) + "\n")


def write_status(command: str, success: bool, exit_code: int, message: str) -> None:
    payload = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "success": success,
        "exit_code": exit_code,
        "message": message[:500],
    }
    try:
        _atomic_write(STATUS_PATH, json.dumps(payload, indent=2) + "\n")
    except OSError:
        # The command's real result is still more important than a diagnostic file.
        pass


def _clean_body_for_summary(body: str) -> str:
    body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    body = re.sub(r"<[^>]+>", "", body)
    kept: list[str] = []
    for line in body.splitlines():
        text = line.strip()
        if not text or text.startswith(("#", "```")):
            continue
        text = re.sub(r"^[-*+]\s+(?:\[[ xX]\]\s*)?", "", text)
        text = re.sub(r"`[^`]+`", "", text)
        text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text).strip()
        if text:
            kept.append(text)
    return " ".join(kept)


def _summary_from_body(frontmatter: dict[str, Any], body: str) -> str:
    if frontmatter.get("type") == "log":
        focus = re.search(r"(?m)^##\s+Focus\s*\n-\s*(.+)$", body)
        if focus:
            return focus.group(1).strip()[:150]
    summary = _clean_body_for_summary(body)
    return summary[:150] + ("..." if len(summary) > 150 else "")


def _relative(path: Path) -> str:
    return path.resolve().relative_to(Path(VAULT_DIR).resolve()).as_posix()


def _root_for(path: Path) -> Path | None:
    resolved = path.resolve()
    for root in CONTENT_DIRS:
        try:
            resolved.relative_to(Path(root).resolve())
            return Path(root)
        except ValueError:
            continue
    return None


def _is_flat_markdown(path: Path) -> bool:
    root = _root_for(path)
    return root is not None and path.suffix.lower() == ".md" and path.parent.resolve() == root.resolve()


def _date_string(value: Any) -> bool:
    if isinstance(value, (date, datetime)):
        return True
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate_frontmatter(frontmatter: dict[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    note_type = frontmatter.get("type")
    if root == CAPTURE_DIR and not note_type:
        return errors  # Raw capture is deliberately valid without a commitment.
    if note_type not in {"note", "log", "project"}:
        return ["type must be one of: note, log, project (raw Capture notes may omit it)"]
    tags = frontmatter.get("tags")
    if note_type in {"note", "log"} and (not isinstance(tags, list) or not all(isinstance(tag, str) and tag for tag in tags)):
        errors.append("tags must be a non-empty YAML list of strings")
    if note_type == "log" and not _date_string(frontmatter.get("date")):
        errors.append("log notes require date in YYYY-MM-DD format")
    if note_type == "project":
        if root not in {CAPTURE_DIR, ACTIVE_DIR, ARCHIVE_DIR}:
            errors.append("project notes must live in Capture/, Active/, or Archive/")
        if frontmatter.get("status") not in {"active", "paused", "completed", "stopped"}:
            errors.append("project status must be active, paused, completed, or stopped")
        if frontmatter.get("priority") not in {"high", "medium", "low"}:
            errors.append("project priority must be high, medium, or low")
        if not _date_string(frontmatter.get("deadline")):
            errors.append("project deadline must be YYYY-MM-DD")
        if not isinstance(frontmatter.get("area"), str) or not frontmatter["area"].strip():
            errors.append("project area must be a non-empty string")
    return errors


def validate_note(path: Path) -> list[str]:
    errors: list[str] = []
    root = _root_for(path)
    if root is None:
        return ["path is outside Zephyr content roots"]
    if not _is_flat_markdown(path):
        return ["notes must be flat Markdown files directly inside a Zephyr content root"]
    if INVALID_FILENAME.search(path.stem) or not path.stem.strip():
        errors.append("filename is empty or contains a Windows-reserved character")
    try:
        content = path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)
    except (OSError, UnicodeError, FrontmatterError) as exc:
        return [str(exc)]
    errors.extend(validate_frontmatter(frontmatter, root))
    return errors


def _iter_notes() -> list[Path]:
    notes: list[Path] = []
    for directory in CONTENT_DIRS:
        if not Path(directory).exists():
            continue
        notes.extend(path for path in sorted(Path(directory).glob("*.md")) if path.name != "Home.md")
    return notes


def validate_vault(machine_readable: bool = False) -> tuple[bool, list[dict[str, Any]]]:
    ensure_roots()
    issues: list[dict[str, Any]] = []
    seen_titles: dict[str, Path] = {}
    for path in _iter_notes():
        for error in validate_note(path):
            issues.append({"path": _relative(path), "error": error})
        key = path.stem.casefold()
        if key in seen_titles:
            issues.append({"path": _relative(path), "error": f"title collides with {_relative(seen_titles[key])}"})
        else:
            seen_titles[key] = path
    if machine_readable:
        print(json.dumps({"valid": not issues, "issues": issues}, indent=2))
    elif issues:
        print("Validation found issues:")
        for issue in issues:
            print(f"  {issue['path']}: {issue['error']}")
    else:
        print(f"Validation passed for {len(_iter_notes())} notes.")
    return not issues, issues


def scan_unprocessed_ideas() -> list[dict[str, Any]]:
    ideas: list[dict[str, Any]] = []
    if not Path(CAPTURE_DIR).exists():
        return ideas
    for path in sorted(Path(CAPTURE_DIR).glob("*.md")):
        try:
            frontmatter, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, FrontmatterError):
            continue
        if frontmatter.get("type") != "log":
            continue
        in_capture = False
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if re.match(r"^##\s+Capture\b", line, flags=re.IGNORECASE):
                in_capture = True
                continue
            if re.match(r"^##\s+", line):
                in_capture = False
            if in_capture:
                match = re.match(r"^\s*-\s*idea:\s*(.+)$", line, flags=re.IGNORECASE)
                if match and "[[" not in match.group(1):
                    ideas.append({"source_log": _relative(path), "line_number": line_number, "text": match.group(1).strip()})
    return ideas


def find_eligible_inbox_notes() -> list[str]:
    """Expose raw captures for user-invoked agent procedures; make no changes."""
    eligible: list[str] = []
    for path in sorted(Path(CAPTURE_DIR).glob("*.md")) if Path(CAPTURE_DIR).exists() else []:
        if path.name == "Home.md" or path.name.endswith(" -- draft.md"):
            continue
        try:
            frontmatter, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, FrontmatterError):
            continue
        if not frontmatter.get("type") and frontmatter.get("triage_status") != "needs_review":
            eligible.append(str(path))
    return eligible


def _as_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def build_review_queue(
    index: dict[str, Any] | None = None,
    validation_issues: list[dict[str, Any]] | None = None,
    link_issues: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a deterministic, read-only work queue without editing notes."""
    index = index or load_index()
    validation_issues = validation_issues or []
    link_issues = link_issues if link_issues is not None else link_report()
    today = date.today()
    items: list[dict[str, Any]] = []

    for issue in validation_issues:
        items.append({
            "kind": "validation",
            "severity": "high",
            "path": issue.get("path", ""),
            "reason": issue.get("error", "validation issue"),
            "action": "review",
        })

    for value in find_eligible_inbox_notes():
        path = Path(value)
        age_days = max(0, (today - datetime.fromtimestamp(path.stat().st_mtime).date()).days)
        items.append({
            "kind": "capture",
            "severity": "medium" if age_days >= 2 else "low",
            "path": _relative(path),
            "reason": "raw capture awaiting triage",
            "age_days": age_days,
            "action": "triage_or_distill",
        })

    for idea in index.get("unprocessed_ideas", []):
        items.append({
            "kind": "idea",
            "severity": "low",
            "path": idea.get("source_log", ""),
            "line_number": idea.get("line_number"),
            "reason": "daily-log idea awaiting review",
            "preview": str(idea.get("text", ""))[:160],
            "action": "expand_or_ignore",
        })

    for entry in index.get("notes", {}).values():
        if entry.get("root") != "Active" or entry.get("type") != "project":
            continue
        status = entry.get("status")
        deadline = _as_date(entry.get("deadline"))
        if status == "paused":
            items.append({
                "kind": "project",
                "severity": "low",
                "path": entry.get("path", ""),
                "reason": "paused project awaiting periodic review",
                "action": "review_status",
            })
        if status == "active" and deadline:
            days = (deadline - today).days
            if days < 0:
                items.append({
                    "kind": "project",
                    "severity": "high",
                    "path": entry.get("path", ""),
                    "reason": f"active project overdue by {abs(days)} day(s)",
                    "action": "review_deadline",
                })
            elif days <= 7:
                items.append({
                    "kind": "project",
                    "severity": "medium",
                    "path": entry.get("path", ""),
                    "reason": f"active project due in {days} day(s)",
                    "action": "review_deadline",
                })

    for issue in link_issues:
        items.append({
            "kind": "link",
            "severity": "medium",
            "path": issue.get("path", ""),
            "reason": f"{issue.get('error', 'link issue')}: {issue.get('link', '')}",
            "action": "review_link",
        })

    rank = {"high": 0, "medium": 1, "low": 2}
    items.sort(key=lambda item: (rank.get(item["severity"], 9), item.get("path", ""), item["kind"]))
    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "authority": "read-only queue; no note or lifecycle state was changed",
        "counts": {
            "total": len(items),
            "high": sum(item["severity"] == "high" for item in items),
            "medium": sum(item["severity"] == "medium" for item in items),
            "low": sum(item["severity"] == "low" for item in items),
        },
        "items": items,
    }
    _atomic_write(REVIEW_QUEUE_PATH, json.dumps(_safe_json(payload), indent=2, ensure_ascii=False) + "\n")
    print(f"Review queue: {len(items)} item(s) written to System/review-queue.json.")
    return payload


def refresh() -> int:
    """Refresh all safe generated state; findings remain proposals for review."""
    _, validation_issues = validate_vault(False)
    index = compile_index()
    links = heal_links()
    build_review_queue(index, validation_issues, links)
    return 0


def compile_index() -> dict[str, Any]:
    ensure_roots()
    notes: dict[str, dict[str, Any]] = {}
    invalid: list[dict[str, str]] = []
    for path in _iter_notes():
        try:
            content = path.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(content)
        except (OSError, UnicodeError, FrontmatterError) as exc:
            invalid.append({"path": _relative(path), "error": str(exc)})
            continue
        errors = validate_frontmatter(frontmatter, _root_for(path) or Path(CAPTURE_DIR))
        invalid.extend({"path": _relative(path), "error": error} for error in errors)
        title = path.stem
        entry = {
            "title": title,
            "path": _relative(path),
            "root": (_root_for(path) or Path(CAPTURE_DIR)).name,
            "type": frontmatter.get("type", "capture"),
            "tags": frontmatter.get("tags", []),
            "summary": _summary_from_body(frontmatter, body),
            "links": [match.strip() for match in WIKILINK.findall(body)],
            "deadline": frontmatter.get("deadline", ""),
            "status": frontmatter.get("status", ""),
            "priority": frontmatter.get("priority", ""),
            "date": frontmatter.get("date", ""),
            "mtime": path.stat().st_mtime,
        }
        if title in notes:
            invalid.append({"path": _relative(path), "error": f"duplicate title: {title}"})
        notes[title] = _safe_json(entry)
    index = {"version": 2, "notes": notes, "unprocessed_ideas": scan_unprocessed_ideas(), "invalid_notes": invalid}
    save_index(index)
    print(f"Indexed {len(notes)} notes; {len(invalid)} validation issue(s).")
    return index


def link_report() -> list[dict[str, str]]:
    index = load_index()
    notes = index.get("notes", {})
    canonical = {title.casefold(): title for title in notes}
    issues: list[dict[str, str]] = []
    for title, entry in notes.items():
        for target in entry.get("links", []):
            actual = canonical.get(target.casefold())
            if actual is None:
                issues.append({"path": entry["path"], "link": target, "error": "broken link"})
            elif actual != target:
                issues.append({"path": entry["path"], "link": target, "error": f"case mismatch; use {actual}"})
    return issues


def heal_links() -> list[dict[str, str]]:
    """Compatibility name: report links only. Repairs require ``fix-links``."""
    issues = link_report()
    if issues:
        print(f"Link report: {len(issues)} issue(s). Run fix-links --approve to repair only case mismatches.")
    else:
        print("Link report: no broken or case-mismatched links.")
    return issues


def fix_links(approve: bool, dry_run: bool) -> int:
    if not approve:
        raise CommandError("fix-links changes note text; rerun with --approve after review")
    index = load_index()
    canonical = {title.casefold(): title for title in index.get("notes", {})}
    changed = 0
    for path in _iter_notes():
        content = path.read_text(encoding="utf-8")
        def replace(match: re.Match[str]) -> str:
            target, display = match.group(1), match.group(2)
            actual = canonical.get(target.strip().casefold())
            if actual and actual != target.strip():
                suffix = f"|{display}" if display else ""
                return f"[[{actual}{suffix}]]"
            return match.group(0)
        revised = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", replace, content)
        if revised != content:
            changed += 1
            print(f"{'Would repair' if dry_run else 'Repaired'}: {_relative(path)}")
            if not dry_run:
                _atomic_write(path, revised)
    if not dry_run:
        compile_index()
    return changed


def _resolve_note(value: str, root: Path) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = Path(VAULT_DIR) / candidate
        if not candidate.exists():
            candidate = Path(root) / value
    if candidate.suffix.lower() != ".md":
        candidate = candidate.with_suffix(".md")
    candidate = candidate.resolve()
    try:
        candidate.relative_to(Path(root).resolve())
    except ValueError as exc:
        raise CommandError(f"note must be inside {Path(root).name}/") from exc
    if not candidate.is_file():
        raise CommandError(f"note does not exist: {_relative(candidate) if candidate.exists() else value}")
    return candidate


def _render_note(frontmatter: dict[str, Any], body: str) -> str:
    return "---\n" + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip() + "\n---\n\n" + body.lstrip("\n")


def _move_note(source: Path, destination_root: Path, frontmatter: dict[str, Any], body: str, dry_run: bool) -> Path:
    destination = Path(destination_root) / source.name
    if destination.exists() and destination.resolve() != source.resolve():
        raise CommandError(f"destination collision: {_relative(destination)}; rename one note and retry")
    if dry_run:
        print(f"Would move {_relative(source)} -> {_relative(destination)}")
        return destination
    content = _render_note(frontmatter, body)
    # Writing the complete destination before removing the source keeps the source
    # recoverable if a disk or rename operation fails.
    _atomic_write(destination, content)
    try:
        source.unlink()
    except OSError as exc:
        raise CommandError(f"destination was written but source remains at {_relative(source)}; remove it manually after verifying {destination.name}: {exc}") from exc
    print(f"Moved {_relative(source)} -> {_relative(destination)}")
    return destination


def activate(note: str, approve: bool, dry_run: bool) -> Path:
    if not approve:
        raise CommandError("activation requires explicit approval: add --approve")
    source = _resolve_note(note, Path(CAPTURE_DIR))
    content = source.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)
    if frontmatter.get("type") != "project":
        raise CommandError("activation requires type: project in the Capture note; triage suggestions are not commitments")
    errors = validate_frontmatter(frontmatter, Path(CAPTURE_DIR))
    if errors:
        raise CommandError("cannot activate invalid project: " + "; ".join(errors))
    return _move_note(source, Path(ACTIVE_DIR), frontmatter, body, dry_run)


def archive(note: str, approve: bool, force: bool, dry_run: bool) -> Path:
    if not approve:
        raise CommandError("archiving requires explicit approval: add --approve")
    source = _resolve_note(note, Path(ACTIVE_DIR))
    frontmatter, body = parse_frontmatter(source.read_text(encoding="utf-8"))
    if frontmatter.get("type") != "project":
        raise CommandError("only project notes may be archived")
    status = frontmatter.get("status")
    if status not in {"completed", "stopped"} and not force:
        raise CommandError("archive requires status: completed or stopped; use --force only after an explicit review")
    errors = validate_frontmatter(frontmatter, Path(ACTIVE_DIR))
    if errors:
        raise CommandError("cannot archive invalid project: " + "; ".join(errors))
    return _move_note(source, Path(ARCHIVE_DIR), frontmatter, body, dry_run)


def promote(note: str, approve: bool, dry_run: bool) -> Path:
    """Move an approved durable note from Capture into Brain without rewriting its body."""
    if not approve:
        raise CommandError("promotion requires explicit approval: add --approve")
    source = _resolve_note(note, Path(CAPTURE_DIR))
    frontmatter, body = parse_frontmatter(source.read_text(encoding="utf-8"))
    if frontmatter.get("type") != "note":
        raise CommandError("promotion requires an approved type: note in Capture")
    errors = validate_frontmatter(frontmatter, Path(CAPTURE_DIR))
    if errors:
        raise CommandError("cannot promote invalid note: " + "; ".join(errors))
    return _move_note(source, Path(BRAIN_DIR), frontmatter, body, dry_run)


def migrate_archive(apply: bool, dry_run: bool) -> int:
    ensure_roots()
    legacy = Path(SYSTEM_DIR) / "Archive"
    candidates = sorted(legacy.glob("*.md")) if legacy.exists() else []
    if not candidates:
        print("No legacy System/Archive Markdown notes to migrate.")
        return 0
    for source in candidates:
        destination = Path(ARCHIVE_DIR) / source.name
        if destination.exists():
            raise CommandError(f"migration collision: {_relative(destination)}")
        print(f"{'Would move' if dry_run or not apply else 'Moving'} {_relative(source)} -> {_relative(destination)}")
    if apply and not dry_run:
        for source in candidates:
            os.replace(source, Path(ARCHIVE_DIR) / source.name)
        compile_index()
    elif not apply:
        print("No files changed. Review the list and rerun with --apply (or use --dry-run explicitly).")
    return len(candidates)


def sync_git() -> int:
    print("Git sync is intentionally not automated by Zephyr v0.3.1. Use your normal, reviewed Git workflow.")
    return 0


def run_mode(mode: str) -> int:
    """Backward-compatible programmatic interface for deterministic maintenance."""
    if mode in {"index", "fast", "all"}:
        compile_index()
        heal_links()
        return 0
    if mode == "sync":
        sync_git()
        return 0
    if mode == "refresh":
        return refresh()
    if mode == "triage":
        print("Triage is an explicit agent procedure, not a core worker command. Read System/PROTOCOL.md.")
        return 2
    print("Unknown mode. Use: refresh, index, validate, health, fix-links, activate, promote, archive, migrate, or sync.")
    return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zephyr deterministic local vault tools")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("index")
    subparsers.add_parser("fast")
    subparsers.add_parser("all")
    subparsers.add_parser("sync")
    subparsers.add_parser("refresh")
    validate = subparsers.add_parser("validate")
    validate.add_argument("--json", action="store_true", dest="as_json")
    subparsers.add_parser("health")
    fix = subparsers.add_parser("fix-links")
    fix.add_argument("--approve", action="store_true")
    fix.add_argument("--dry-run", action="store_true")
    for name in ("activate", "promote", "archive"):
        command = subparsers.add_parser(name)
        command.add_argument("note")
        command.add_argument("--approve", action="store_true")
        command.add_argument("--dry-run", action="store_true")
        if name == "archive":
            command.add_argument("--force", action="store_true")
    migrate = subparsers.add_parser("migrate")
    migrate.add_argument("--apply", action="store_true")
    migrate.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    command = args.command or "index"
    try:
        if command in {"index", "fast", "all", "sync", "refresh"}:
            code = run_mode(command)
        elif command == "validate":
            code = 0 if validate_vault(args.as_json)[0] else 1
        elif command == "health":
            valid, _ = validate_vault(False)
            compile_index()
            links = heal_links()
            code = 0 if valid and not links else 1
        elif command == "fix-links":
            fix_links(args.approve, args.dry_run)
            code = 0
        elif command == "activate":
            activate(args.note, args.approve, args.dry_run)
            if not args.dry_run:
                compile_index()
            code = 0
        elif command == "promote":
            promote(args.note, args.approve, args.dry_run)
            if not args.dry_run:
                compile_index()
            code = 0
        elif command == "archive":
            archive(args.note, args.approve, args.force, args.dry_run)
            if not args.dry_run:
                compile_index()
            code = 0
        elif command == "migrate":
            migrate_archive(args.apply, args.dry_run)
            code = 0
        else:
            code = run_mode(command)
        write_status(command, code == 0, code, "completed" if code == 0 else "completed with reported issues")
        return code
    except (CommandError, FrontmatterError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        write_status(command, False, 1, str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
