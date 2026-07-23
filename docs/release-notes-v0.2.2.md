# Zephyr v0.2.2 Release Notes

## Active dashboard

- Rebuilt `Active/Active.md` as a Zephyr editorial dashboard with the shared navigation, typography, bento statistics, project cards, muted status colours, and responsive layout.
- Added at-a-glance counts for active, paused, deadline-free, and next-seven-day projects.
- Kept lifecycle boundaries intact: the dashboard only reads project metadata and never changes commitments.

## Watcher assessment

`run-watcher` remains available as an optional local utility in this release. It only rebuilds the generated index after a Markdown edit; it does not validate, write notes, update Dataview, or invoke an agent. For small personal vaults it is not necessary: explicit `index` runs are sufficient before a review or agent task.

The recommended next simplification is to remove the watcher from the default install and retain only the explicit index command, unless a user demonstrates a large-vault or external-tool workflow that needs continuously fresh `System/index.json`.
