# Zephyr Protocol v0.2

This is the canonical, agent-neutral operating contract for a Zephyr vault. Agent-specific files are adapters; they must link here rather than duplicate or override these rules.

## Vault roots

Only these roots hold Zephyr content:

| Root | Purpose | Authority |
| --- | --- | --- |
| `Capture/` | Raw or unconfirmed input | Human or agent may add; raw notes may have no `type`. |
| `Active/` | Work the user explicitly chose to advance | Enter only through approved activation. |
| `Brain/` | Durable, reusable knowledge | Agents may propose organization; preserve prose. |
| `Archive/` | Completed, stopped, or superseded records | Enter only through approved archiving. |
| `System/` | Scripts, templates, schemas, indexes, and status | Operational assets, not personal knowledge. |

Notes are flat Markdown files with unique Windows-safe names. Wikilinks are flat: `[[Note Name]]`, never folder-qualified.

## Lifecycle

```text
Capture → agent proposes metadata/destination → human approves → deterministic command applies → index/status refresh
Active project (completed or stopped) → human approves → archive command applies → index/status refresh
```

An agent’s `suggested_type: project`, title, tag, or destination is a proposal, not permission to create an active commitment. It must not set a deadline, priority, project status, move a note to `Active/`, archive a note, delete a note, or rewrite human prose without explicit human approval.

## Frontmatter

Frontmatter is standard YAML and is parsed with PyYAML. Invalid YAML and schema errors are reported; the worker never rewrites a note body simply to repair them.

```yaml
# durable knowledge
type: note
tags: [topic]

# daily or meeting log
type: log
date: 2026-07-22
tags: [daily]

# project awaiting or in an approved lifecycle state
type: project
status: active # active | paused | completed | stopped
priority: medium # high | medium | low
deadline: 2026-08-31
area: "[[Area Name]]"
tags: [project]
```

## Deterministic commands

```bash
python3 System/zephyr-worker.py validate
python3 System/zephyr-worker.py index
python3 System/zephyr-worker.py health
python3 System/zephyr-worker.py activate "Capture/Project.md" --approve --dry-run
python3 System/zephyr-worker.py activate "Capture/Project.md" --approve
python3 System/zephyr-worker.py archive "Active/Project.md" --approve --dry-run
python3 System/zephyr-worker.py archive "Active/Project.md" --approve
python3 System/zephyr-worker.py fix-links --approve --dry-run
```

`activate` validates a complete project before moving it from `Capture/` to `Active/`. `archive` accepts only completed/stopped projects unless the human uses `--force` after review. Both detect collisions, write a complete destination before removing the source, and rebuild the index. `--dry-run` changes nothing.

The optional watcher merely debounces local Markdown edits and runs `index`; it never calls an agent or a network API. `fix-links` is explicit; ordinary indexing reports broken links and case mismatches instead of changing prose.

## Governance

- **AUTO:** create empty roots; parse, validate, index, report links/status; run the local-only watcher.
- **PROPOSE:** semantic triage, tags, titles, links, project metadata, prose edits, moves, archive, deletion, status/deadline/priority changes.
- **NEVER:** direct LLM API calls or API-key handling in Zephyr core; hidden cloud fallback; watcher-triggered agents; rewriting old Git history; committing personal vault content to the public template.

## Definition of done

For a vault change: required notes have valid frontmatter; `validate` and `index` succeed; `System/index.json` and `System/status.json` reflect the result; and any consequential action had explicit approval.
