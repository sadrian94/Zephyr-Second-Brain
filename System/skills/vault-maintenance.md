---
type: skill
id: vault-maintenance
trigger: on-change-or-on-demand
automation: observe
safe_to_schedule: true
writes: [System]
tags: [local, procedure, maintenance]
---
# Vault Maintenance

## Purpose

Keep generated state current and expose mechanical problems early.

Run:

```bash
python3 System/zephyr-worker.py refresh
```

This may run automatically through the local watcher. It validates frontmatter, rebuilds the index, reports links, and writes the review queue. It may create or replace generated files under `System/`; it must not edit notes.

Case-only link repair still requires `fix-links --approve --dry-run` followed by `fix-links --approve`. Lifecycle moves remain separate approved operations.
