---
name: zephyr-second-brain
description: Operate, organize, migrate, validate, and review a Zephyr Second Brain vault. Use when the task concerns Capture, Active, Brain, Archive, System/index.json, frontmatter, project activation or archiving, link health, or Zephyr agent procedures.
---

# Zephyr Second Brain

Use `System/PROTOCOL.md` as the authoritative contract. `System/skills/` contains optional vault procedures; it is not a Codex skill directory.

## Start safely

1. Confirm the vault root contains `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
2. Read `System/PROTOCOL.md` completely.
3. Run `python3 System/zephyr-worker.py refresh`, then inspect `System/index.json` and `System/review-queue.json` before inferring vault state or attention priorities.
4. Run `python3 System/zephyr-worker.py validate` before applying a lifecycle change.

## Choose the action

- For raw captures or semantic organization, prepare a proposal. Preserve human prose. Use `suggested_type`, `suggested_destination`, and `triage_status: proposed` for an inferred project.
- For approved activation, require complete project YAML and use `activate --approve --dry-run` before `activate --approve`.
- For an approved durable or distilled note, require valid `type: note` YAML and use `promote --approve --dry-run` before `promote --approve`.
- For approved completed/stopped work, use `archive --approve --dry-run` before `archive --approve`.
- For vault health, use `health`; indexing only reports link issues. Use `fix-links --approve --dry-run` only after reviewing case-only repairs.
- For a legacy archive migration, read `docs/migration-v0.2.md` and run `migrate --dry-run` before `migrate --apply`.

## Boundaries

Never treat a proposal as authorization. Do not activate, archive, delete, rewrite human prose, or set project status, priority, or deadlines without explicit approval. Do not invoke an LLM API or configure credentials for Zephyr core. The watcher is local-only and never invokes an agent.

Observe automation may write generated state under `System/`. Draft automation is opt-in and may create only a new collision-safe `-- draft.md` proposal in `Capture/` while preserving its source. Read `System/AUTOMATION.md` before scheduled or unattended work.
