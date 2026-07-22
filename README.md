# Zephyr Second Brain

Zephyr is a local-first, Markdown-based second-brain protocol for Obsidian. Version 0.2 is manual-first: agents can prepare proposals, while a human explicitly approves commitments and a deterministic local worker applies them.

Read the [protocol](System/PROTOCOL.md), [capability matrix](docs/capabilities.md), and [v0.1 → v0.2 migration guide](docs/migration-v0.2.md) before moving an existing vault.

## What it does

- Uses five roots: `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
- Validates standard YAML frontmatter and builds `System/index.json` locally.
- Moves a reviewed project only through explicit, collision-safe `activate` and `archive` commands.
- Provides an optional local watcher that runs validation/index reporting after a debounce.

Zephyr does not invoke an agent from the watcher, call an LLM API, retain API credentials, automatically activate projects, automatically archive projects, or automatically rewrite note prose.

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 init-zephyr.py              # creates a personal vault at ~/Obsidian/Zephyr
cd ~/Obsidian/Zephyr
python3 System/zephyr-worker.py validate
python3 System/zephyr-worker.py index
```

To use this checkout deliberately as a vault instead:

```bash
python3 init-zephyr.py --here
python3 System/zephyr-worker.py validate
```

Dataview and the supplied CSS snippet remain optional presentation tools; they are not the source of truth.

## Everyday flow

1. Write freely in `Capture/`.
2. Ask an agent to prepare a proposal if useful. The agent follows `System/PROTOCOL.md`; it must not treat a proposal as authorization.
3. Review a proposed project. Complete the project YAML (status, priority, deadline, area), then preview and apply its move:

   ```bash
   python3 System/zephyr-worker.py activate "Capture/Project.md" --approve --dry-run
   python3 System/zephyr-worker.py activate "Capture/Project.md" --approve
   ```

4. When completed or stopped, update its status and archive it explicitly:

   ```bash
   python3 System/zephyr-worker.py archive "Active/Project.md" --approve --dry-run
   python3 System/zephyr-worker.py archive "Active/Project.md" --approve
   ```

5. Use `health` to see validation and link issues. `fix-links --approve --dry-run` previews only case-safe wikilink repairs.

## Privacy and boundaries

The core works offline after dependencies are installed. It sends no note content to an LLM API and has no API-key setting or cloud fallback. External agent use is separate and user-controlled. Keep personal vaults and `System/config.json` outside the public template remote.

## Layout

```text
Zephyr/
├── Capture/     # raw or unconfirmed material
├── Active/      # explicitly approved active projects
├── Brain/       # durable knowledge
├── Archive/     # completed/stopped records
└── System/      # protocol, scripts, templates, index, status
```

Chinese README: [README-ZH.md](README-ZH.md)
