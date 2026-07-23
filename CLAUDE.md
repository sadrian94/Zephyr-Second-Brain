# Zephyr Claude Adapter

This is a thin adapter. The authoritative rules are in [System/PROTOCOL.md](System/PROTOCOL.md).

1. Treat the vault root as the directory containing `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
2. Read `System/PROTOCOL.md`, run `python3 System/zephyr-worker.py index`, then use `System/index.json` as the global map.
3. Preserve human prose and treat triage, tags, links, titles, metadata, and drafts as proposals.
4. Require explicit human approval before activation, archiving, deletion, prose changes, or project status, priority, and deadline changes.
5. Zephyr has no permanent agent hierarchy. Only one agent may mutate the vault during a task or session; reviewers and specialists are read-only by default.

Personal configuration is optional and must not contain API credentials for Zephyr core. Never commit personal notes from a private vault to the public template.
