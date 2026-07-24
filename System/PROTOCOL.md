# Zephyr Protocol v0.3.1

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
Approved durable note in Capture → human approves → promote command applies → Brain
Active project (completed or stopped) → human approves → archive command applies → index/status refresh
```

An agent’s `suggested_type: project`, title, tag, or destination is a proposal, not permission to create an active commitment. It must not set a deadline, priority, project status, move a note to `Active/`, archive a note, delete a note, or rewrite human prose without explicit human approval.

## Agent coordination

Zephyr does not define permanent primary or secondary agents. For each task or session, one agent may act as the active operator. Other agents may participate as read-only reviewers or bounded specialists.

**One writer at a time; multiple readers allowed.** The active operator may search the vault, prepare proposals, run deterministic read-only commands, and apply an explicitly approved command. A reviewer inspects proposals or results without mutating the vault. A specialist performs bounded work such as research, migration review, documentation review, or code implementation; the role grants no permanent authority.

Agents must refresh `System/index.json` before making vault-state claims and after approved lifecycle changes. The human remains the sole approval authority for activation, archiving, deletion, prose changes, and project metadata changes.

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
python3 System/zephyr-worker.py refresh
python3 System/zephyr-worker.py validate
python3 System/zephyr-worker.py index
python3 System/zephyr-worker.py health
python3 System/zephyr-worker.py activate "Capture/Project.md" --approve --dry-run
python3 System/zephyr-worker.py activate "Capture/Project.md" --approve
python3 System/zephyr-worker.py promote "Capture/Distilled Note.md" --approve --dry-run
python3 System/zephyr-worker.py promote "Capture/Distilled Note.md" --approve
python3 System/zephyr-worker.py archive "Active/Project.md" --approve --dry-run
python3 System/zephyr-worker.py archive "Active/Project.md" --approve
python3 System/zephyr-worker.py fix-links --approve --dry-run
```

`activate` validates a complete project before moving it from `Capture/` to `Active/`. `promote` validates an approved `type: note` before moving it from `Capture/` to `Brain/`. `archive` accepts only completed/stopped projects unless the human uses `--force` after review. All detect collisions, write a complete destination before removing the source, and rebuild the index. `--dry-run` changes nothing.

## Automation

Zephyr separates automation by consequence. See `System/AUTOMATION.md` for the complete contract.

- **Observe:** may run unattended and write only generated state under `System/`.
- **Draft:** a direct human request authorizes one isolated draft; scheduled drafts require explicit opt-in. Drafts may create a new collision-safe `-- draft.md` proposal in `Capture/`; they may not alter the source.
- **Commit:** always requires current human approval and a deterministic command where available.

`refresh` is the safe observe-level entry point. It validates, indexes, reports links, and creates `System/review-queue.json`. The queue is evidence for review, not authority to change notes.

The local watcher may invoke `refresh`, but never an agent. A user may directly ask an agent to capture, triage, expand, or distill a named item; this authorizes only the requested new raw note or companion draft. A user-configured external scheduler may invoke a bundled draft skill only when draft automation is explicitly enabled. Neither path can convert a draft into a commitment.

The optional watcher merely debounces local Markdown edits and runs `refresh` or `index`; it never calls an agent or a network API. `fix-links` is explicit; ordinary indexing reports broken links and case mismatches instead of changing prose.

## Governance

- **AUTO:** create empty roots; parse, validate, index, report links/status; create the review queue; run the local-only watcher.
- **DIRECT DRAFT:** a current user request may create one new raw Capture or companion draft while preserving its named source.
- **OPT-IN DRAFT:** create a separate collision-safe proposal in `Capture/` while preserving its source.
- **PROPOSE:** semantic triage, tags, titles, links, project metadata, prose edits, moves, archive, deletion, status/deadline/priority changes.
- **NEVER:** direct LLM API calls or API-key handling in Zephyr core; hidden cloud fallback; watcher-triggered agents; rewriting old Git history; committing personal vault content to the public template.

## Definition of done

For a vault change: required notes have valid frontmatter; `validate` and `index` succeed; `System/index.json` and `System/status.json` reflect the result; and any consequential action had explicit approval.
