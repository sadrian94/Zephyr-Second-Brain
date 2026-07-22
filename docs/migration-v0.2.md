# Migrating a v0.1 Vault to v0.2

1. Make a recoverable backup or commit in the personal vault.
2. Update the template assets, then create the new roots without moving notes:

   ```bash
   python3 init-zephyr.py --update
   python3 System/zephyr-worker.py migrate --dry-run
   ```

3. Review the proposed moves from `System/Archive/` to root `Archive/`. Apply only when the list is correct:

   ```bash
   python3 System/zephyr-worker.py migrate --apply
   ```

4. Review project candidates in `Brain/` manually. Do not move them merely because they are marked active. For each project you choose to advance, move it to `Capture/`, complete its frontmatter, then use `activate --approve`.
5. Run `validate`, `health`, and `index`. Resolve malformed YAML, duplicate names, and reported broken links before removing old compatibility material.

The migration command only moves Markdown files from the legacy archive and checks collisions first. It does not delete the legacy directory, infer active work, or modify note bodies.
