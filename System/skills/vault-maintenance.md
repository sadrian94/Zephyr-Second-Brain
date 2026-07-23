---
type: skill
frequency: weekly
tags: [agent, procedure, maintenance]
---
# Vault Maintenance Procedure

Run `python3 System/zephyr-worker.py health` and report invalid frontmatter, naming collisions, and link issues. Indexing reports only; it does not repair links.

You may prepare a list of case-only link repairs or completed/stopped projects, but do not change files, move notes, or delete attachments automatically. The human reviews the list and may run `fix-links --approve` or `archive --approve` (prefer `--dry-run`).
