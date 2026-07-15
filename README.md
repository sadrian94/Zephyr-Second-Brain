# Zephyr Second Brain

> Named after **Zephyrus**, the Greek god of the West Wind. Zephyr symbolizes a system that runs as lightly and imperceptibly as a gentle breeze in the background, yet possesses the strength to sweep away all chaotic formatting, cognitive noise, and redundant tasks.
>
> 📖 Read the full **[Zephyr Philosophy & Positioning](./docs/philosophy-and-positioning.md)** document for a deep dive into our flow-first design and on-demand architecture.

Zephyr is an extremely lightweight, imperceptible, and flow-first Obsidian-based Second Brain built for cross-device sync and multi-agent collaboration, designed specifically to serve the **Hermes-agent** ecosystem. It minimizes cognitive overhead, allowing human minds to remain in pure creative flow while background workers and AI agents handle note organization, linkage, and curation.

---

## 🎯 Positioning & Core Philosophy

- **Lightweight & Invisible**: Operates silently in the background like a breeze. It doesn't force complex directory micro-management, keeping you in the flow state.
- **Hermes-Agent Native**: Tailored as the ultimate memory and knowledge base for Hermes-agent, providing clean metadata, simple APIs, and a unified index.
- **Local-First & Plain-Text**: Built entirely on flat folders of standard Markdown files and WikiLinks (`[[Note Name]]`). It is fully compatible with Obsidian.
- **Capture-First, Classify-Later**: Humans record raw thoughts effortlessly in the Capture inbox. Local workers and AI agents classify, tag, format, and organize them into the Brain.
- **Bi-directional Active Growth**: Through automated nightly "dreams" and weekly "reviews," the vault actively heals broken links, generates semantic associations, and clusters related notes into Portals/MOCs.

---

## 📂 Vault Directory Structure

All notes in the vault reside in exactly one of three folders:

```
Zephyr/
├── Capture/          # The Ingestion Inbox
│   ├── YYYY-MM-DD.md # Daily logs, task tracking, and quick captures
│   └── *.md          # Raw clippings, thoughts, book excerpts
├── Brain/            # The Permanent Knowledge Base
│   ├── Brain.md      # The central entry portal dashboard
│   └── *.md          # Active projects, Evergreen notes, Knowledge Areas, and MOCs
└── System/           # Configuration, Routines, and Automation
    ├── Archive/      # Archived and completed projects
    ├── skills/       # AI agent routines (Dream Mode, Slow Mode, etc.)
    ├── templates/    # Templates for notes, projects, logs, and sources
    ├── index.json    # The local metadata index cache
    └── zephyr-*      # Local background scripts (watcher, worker)
```

---

## ⚙️ Automation & Routines

Zephyr is powered by a local Python daemon and periodic AI Agent routines:

1. **Local Watcher & Worker** (`zephyr-watcher.py` & `zephyr-worker.py`):
   - Runs in the background (via `run-watcher.bat`).
   - Automatically processes new files in `Capture/`, applies standard metadata templates, fixes internal case-mismatched links, compiles `System/index.json`, and handles git auto-commits.
2. **Dream Mode (Nightly)**:
   - Evaluates notes modified in the last 24 hours.
   - Suggests semantic connections under `## Suggested Connections` without altering human-written content.
   - Automatically drafts Map of Contents (MOCs) when clusters of related notes emerge.
3. **Slow Mode (Weekly Review)**:
   - Runs every Monday morning.
   - Audits vault health (orphan notes, broken links).
   - Generates a high-level project briefing, highlights deadlines, and posts updates to the configured Discord channel.

---

## ⚖️ Governance Model

To balance AI autonomy with user control over their knowledge base, Zephyr follows a strict three-tier governance system:

- **`AUTO` (Automated Actions)**: AI can automatically classify notes from `Capture/` to `Brain/`, add standard tags, heal broken links, compile index metadata, and commit changes to Git.
- **`PROPOSE` (Review Needed)**: For destructive or body-modifying actions—such as deleting files, changing project statuses/deadlines, or editing human-written text—the AI must generate a draft proposal (suffix `-- draft.md`) or ask for user confirmation.
- **`NEVER` (Strictly Prohibited)**: AI is forbidden from modifying `.obsidian/` configuration files, exposing API keys/secrets, or altering Git commits older than the current session branch.

---

## 🚀 Setup & Prerequisites

1. **Obsidian Integration**:
   - Install the **Dataview** community plugin and enable **Enable DataviewJS** in settings.
   - Copy `System/zephyr-dashboard.css` into your Obsidian CSS snippets folder and activate it under `Settings -> Appearance -> CSS Snippets`.
2. **Background Automation**:
   - Run `run-watcher.bat` to launch the file watcher that monitors the `Capture/` directory for incoming thoughts.

---

## 📖 Vault Documentation

Explore the detailed manuals inside the `docs/` folder:
- 💡 **[Zephyr Philosophy & Positioning](./docs/philosophy-and-positioning.md)**: Flow-first design principles.
- ⚙️ **[Technical Architecture Manual](./docs/architecture.md)**: Script interactions and `index.json` details.
- 🎯 **[Project Management Guide](./docs/project-management.md)**: Setting up and automating project lifecycles.
