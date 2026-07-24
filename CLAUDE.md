# Zephyr Claude Adapter

This is a thin adapter. The authoritative rules are in [System/PROTOCOL.md](System/PROTOCOL.md).

1. Treat the vault root as the directory containing `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
2. Read `System/PROTOCOL.md` and `System/AUTOMATION.md`, run `python3 System/zephyr-worker.py refresh`, then use `System/index.json` and `System/review-queue.json` as the global map and attention queue.
3. Preserve human prose and treat triage, tags, links, titles, metadata, and drafts as proposals.
4. A direct user request to capture, triage, expand, or distill a named item authorizes one new collision-safe raw note or companion draft in `Capture/`; preserve the source.
5. Require explicit human approval before activation, promotion, archiving, deletion, prose changes, or project status, priority, and deadline changes.
6. Zephyr has no permanent agent hierarchy. Only one agent may mutate the vault during a task or session; reviewers and specialists are read-only by default.
7. Scheduled draft work is allowed only after explicit opt-in, must preserve its source, and may create only a collision-safe `-- draft.md` proposal in `Capture/`.

Personal configuration is optional and must not contain API credentials for Zephyr core. Never commit personal notes from a private vault to the public template.
