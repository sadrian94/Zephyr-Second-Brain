# Updating a v0.2 Vault to v0.2.1

Version 0.2.1 removes the permanent primary/secondary-agent model. It does not move, rewrite, activate, archive, or delete personal notes.

1. Make a recoverable backup or commit in the personal vault.
2. Update the local Zephyr template, then run:

   ```bash
   python3 init-zephyr.py --update
   python3 System/zephyr-worker.py validate
   python3 System/zephyr-worker.py index
   python3 System/zephyr-worker.py health
   ```

3. Keep legacy `primary_agent_name` and `secondary_agent_name` values in `System/config.json` if they are already present. Zephyr ignores them and preserves unknown configuration fields; no manual rewrite is required.
4. Review the refreshed `AGENTS.md`, `GEMINI.md`, and optional `CLAUDE.md`. For any task or session, appoint at most one active writer; use other agents only as read-only reviewers or bounded specialists.

The update refreshes system assets and adapters. It does not alter personal notes or overwrite `System/config.json`.
