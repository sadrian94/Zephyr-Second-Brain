# Zephyr Gemini Adapter

This is a thin adapter. The authoritative rules are in [System/PROTOCOL.md](System/PROTOCOL.md).

1. Treat the vault root as the directory containing `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
2. Read `System/PROTOCOL.md` and `System/AUTOMATION.md`, run `python3 System/zephyr-worker.py refresh`, then use `System/index.json` and `System/review-queue.json` as the global map and attention queue.
3. You may prepare triage, tags, links, titles, or drafts. Mark an inferred project with proposal fields such as `suggested_type: project`, `suggested_destination: Active`, and `triage_status: proposed`.
4. Do not activate, archive, delete, rewrite human prose, set project status/priority/deadline, invoke a network API, or run a watcher-triggered action without the user’s explicit approval.
5. When a move is approved, use the worker’s `activate` or `archive` command with `--approve`; prefer `--dry-run` first.
6. Zephyr has no permanent agent hierarchy. Only one agent may mutate the vault during a task or session; reviewers and specialists are read-only unless the human explicitly authorizes an approved command.
7. Scheduled draft work is allowed only after explicit opt-in, must preserve its source, and may create only a collision-safe `-- draft.md` proposal in `Capture/`.

Personal configuration is optional and must not contain API credentials for Zephyr core. Never commit personal notes from a private vault to the public template.
