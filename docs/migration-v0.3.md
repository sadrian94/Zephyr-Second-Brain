# Updating a v0.2 Vault to v0.3.1

Version 0.3.1 adds consequence-based automation and an agent-first interface without changing personal notes or `System/config.json`.

1. Make a recoverable backup or commit in the personal vault.
2. Update template assets:

   ```bash
   python3 init-zephyr.py --update
   python3 System/zephyr-worker.py refresh
   python3 System/zephyr-worker.py health
   ```

3. Review `System/review-queue.json`. It is generated evidence, not a command queue.
4. Keep draft automation disabled unless an external agent platform is deliberately configured. To opt in, copy `System/automation.example.json` to `System/automation.json` and enable only the desired draft skills.
5. Use `promote --approve --dry-run` and `promote --approve` for a reviewed durable note in `Capture/` with valid `type: note` frontmatter.

The watcher now runs `refresh` by default. Set `on_change` to `index` in `System/automation.json` for the previous lightweight behavior. `init-zephyr.py --update` does not delete retired `System/skills` files from an existing personal vault; remove them manually after review if you want the consolidated four-procedure set.
