# Zephyr Second Brain

Zephyr is a local-first, Markdown-based second brain for Obsidian. Its primary interface is a conversation with an AI agent; deterministic CLI commands are the auditable transaction layer behind consequential changes.

Start with the [usage guide](docs/usage-guide.md). The detailed rules are in the [protocol](System/PROTOCOL.md) and [automation model](System/AUTOMATION.md); see also the [capability matrix](docs/capabilities.md), [v0.3.1 release notes](docs/release-notes-v0.3.1.md), and [update guide](docs/migration-v0.3.md).

## What it does

- Uses five roots: `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
- Lets you tell an agent to capture, triage, expand, distill, review, or approve a named item in natural language.
- Validates standard YAML frontmatter and builds `System/index.json` locally.
- Builds `System/review-queue.json` from raw captures, dated ideas, project deadlines, validation findings, and link issues.
- Moves a reviewed project only through explicit, collision-safe `activate` and `archive` commands.
- Promotes an approved distilled note from `Capture/` to `Brain/` through `promote --approve`.
- Provides an optional local watcher that runs the safe `refresh` pipeline after a debounce.

Zephyr does not invoke an agent from the watcher, call an LLM API, retain API credentials, automatically activate/promote/archive material, or automatically rewrite note prose.

Zephyr is agent-neutral: one agent operates at a time, and optional reviewers or specialists remain bounded and read-only by default. It does not assign permanent agent rank or require more than one agent.

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 init-zephyr.py              # creates a personal vault at ~/Obsidian/Zephyr
cd ~/Obsidian/Zephyr
python3 System/zephyr-worker.py validate
python3 System/zephyr-worker.py refresh
```

To use this checkout deliberately as a vault instead:

```bash
python3 init-zephyr.py --here
python3 System/zephyr-worker.py validate
```

Dataview and the supplied CSS snippet remain optional presentation tools; they are not the source of truth.

## Agent-first everyday flow

1. Tell the agent what you want: “Capture this idea,” “distill this clipping,” “show me this week’s review,” or “what needs my decision?”
2. The agent may create the requested raw Capture or a separate draft, then refresh the queue. It preserves the source and labels its inference.
3. When a proposal is right, tell the agent explicitly: “I approve this as a project” or “Promote this note to Brain.” The agent validates, previews, and runs the deterministic command for you.
4. You may also run the same commands yourself. For a project, the transaction is:

   ```bash
   python3 System/zephyr-worker.py activate "Capture/Project.md" --approve --dry-run
   python3 System/zephyr-worker.py activate "Capture/Project.md" --approve
   ```

5. For an approved durable or distilled note, the transaction is:

   ```bash
   python3 System/zephyr-worker.py promote "Capture/Distilled Note.md" --approve --dry-run
   python3 System/zephyr-worker.py promote "Capture/Distilled Note.md" --approve
   ```

6. When a project is completed or stopped, the transaction is:

   ```bash
   python3 System/zephyr-worker.py archive "Active/Project.md" --approve --dry-run
   python3 System/zephyr-worker.py archive "Active/Project.md" --approve
   ```

7. Use `health` for a strict diagnostic result. `fix-links --approve --dry-run` previews only case-safe wikilink repairs.

Direct conversation authorizes only the specific Capture or companion draft you requested. It never grants standing approval for activation, promotion, archiving, deletion, prose changes, or project metadata.

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

Chinese README: [README-ZH.md](README-ZH.md) · Chinese usage guide: [docs/usage-guide-zh.md](docs/usage-guide-zh.md)
