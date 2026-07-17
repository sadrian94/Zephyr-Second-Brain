# Zephyr Second Brain

> Named after **Zephyrus**, the Greek god of the West Wind. Zephyr is a lightweight, flow-first Obsidian second brain for humans + Hermes-agent.

Deep dives:
- [Philosophy & Positioning](./docs/philosophy-and-positioning.md)
- [Architecture](./docs/architecture.md)
- [Hermes Cron Inbox Triage](./docs/hermes-cron.md)
- [Project Management](./docs/project-management.md)

Zephyr keeps you in capture flow. Hermes handles semantic inbox triage through its configured provider; local workers handle deterministic indexing, link healing, and maintenance.

---

## Prerequisites (Obsidian)

### Required (dashboards will not work without these)

| Component | Why |
|-----------|-----|
| **[Dataview](https://github.com/blacksmithgu/obsidian-dataview)** community plugin | Powers `Home.md`, `Capture.md`, `Brain.md` via DataviewJS |
| **Enable DataviewJS** in Dataview settings | Dashboards execute JS layouts |
| **CSS snippet `zephyr-dashboard`** | Layout/styles for the bento dashboard (`System/zephyr-dashboard.css` → `.obsidian/snippets/`) |

Install Dataview from Obsidian → Settings → Community plugins. This template does **not** vendor plugin binaries in git.

### Optional (personal preference — not required, not tracked)

These are fine for a personal vault but are **not** part of the Zephyr template:

- Templater
- Calendar
- Obsidian Git
- Excalidraw
- QuickAdd
- Icon Folder
- any other community plugins

Plugin folders under `.obsidian/plugins/**` are gitignored so personal tastes do not land on GitHub.

---

## 5-Minute Quickstart

**Recommended workflow:** keep this GitHub repo as a **template**, and install your personal second brain to the default vault path `~/Obsidian/Zephyr`. That keeps personal notes and secrets out of git by design.

### Option A — Default install to `~/Obsidian/Zephyr` (recommended)

```bash
# 1) Install deps (from this repo)
python3 -m pip install -r requirements.txt

# 2) Initialize personal vault at ~/Obsidian/Zephyr
#    (copies templates/scripts, writes System/config.json, enables Dataview/CSS flags)
python3 init-zephyr.py

# 3) Build the index (no API key required)
python3 ~/Obsidian/Zephyr/System/zephyr-worker.py index

# 4) Start the background watcher from the personal vault
cd ~/Obsidian/Zephyr
./run-watcher.sh
# Windows: run-watcher.bat
```

Open `~/Obsidian/Zephyr` as an Obsidian vault, then:
1. Install/enable **Dataview** and turn on **Enable DataviewJS**.
2. Enable CSS snippet **zephyr-dashboard** in Settings → Appearance → CSS Snippets.
3. Open `Home.md`.

Optional: put personal defaults in repo-root `config_local.json` (gitignored) before running `init-zephyr.py`; they will be copied into the personal vault's `System/config.json`.

### Update an existing vault safely

Develop system changes in this template repo, then update the personal vault from the repo root:

```bash
python3 init-zephyr.py --update
```

`--update` refreshes Zephyr-owned assets only: the watcher/worker launchers, `System/` scripts, design/CSS, skills, templates, and the three dashboards (`Home.md`, `Capture/Capture.md`, `Brain/Brain.md`). It preserves `System/config.json`, all other personal notes in `Capture/` and `Brain/`, community-plugin binaries, and existing Obsidian preferences. It then rebuilds `System/index.json`.

### Option B — Use this repo as the vault (`--here`)

Only if you intentionally want the template checkout itself to act as the vault:

```bash
python3 init-zephyr.py --here
python3 System/zephyr-worker.py index
./run-watcher.sh
```

`--here` writes gitignored `System/config.json` only; it does **not** rewrite tracked `AGENTS.md` / `GEMINI.md` with personal names.

### Optional: Hermes inbox triage

Zephyr does not require a direct model API key in `System/config.json`. Configure a Hermes cron job in the profile that already has your preferred provider or OAuth session, set its `workdir` to the personal vault root, and require it to read `System/skills/inbox-triage.md` before acting. The local worker remains available without Hermes for indexing and link healing.

### Privacy note (important for GitHub)

This repo is a **template**, not a personal vault dump:
- Personal second brain lives at `~/Obsidian/Zephyr` (default) and should stay off the public remote.
- Tracked in the template: dashboards (`Home.md`, `Capture/Capture.md`, `Brain/Brain.md`), templates, skills, scripts, minimal `.obsidian` config + `zephyr-dashboard` CSS.
- Gitignored: `System/config.json`, `config_local.json`, personal notes under `Capture/**` and `Brain/**` (except the two dashboards), `System/index.json`, `IDEA.md`, and **all** `.obsidian/plugins/**` binaries.
- `AGENTS.md` / `GEMINI.md` stay as `{{placeholder}}` templates so personal names never leak into git.

---

## Positioning

- **Lightweight & Invisible**: no forced folder micro-management.
- **Hermes-Agent Native**: clean frontmatter + `System/index.json` context cache.
- **Local-First & Plain-Text**: Markdown + flat wikilinks (`[[Note Name]]`).
- **Capture-First, Classify-Later**: humans dump thoughts; workers/agents organize.
- **Active Growth**: dream-mode (nightly) and slow-mode (weekly) skills for healing and review.

---

## Vault Layout

```
Zephyr/
├── Capture/          # Inbox + daily logs
├── Brain/            # Projects, evergreen notes, areas, MOCs
└── System/           # Config, templates, skills, index, scripts
    ├── DESIGN.md     # Design system (binding for dashboards/CSS)
    ├── index.json    # Compiled metadata cache
    ├── skills/       # Agent routines
    ├── templates/
    └── zephyr-*.py   # Watcher + worker
```

---

## Automation

1. **Watcher / Worker** (`zephyr-watcher.py`, `zephyr-worker.py`)
   - Watches `Capture/` + `Brain/`
   - Compiles `System/index.json`
   - Heals case-mismatched wikilinks
   - Runs git sync only through the explicit `python3 System/zephyr-worker.py sync` command
2. **Hermes Inbox Triage (scheduled skill)**: classifies eligible raw captures using Hermes's configured provider, preserves body text, and indexes the result.
3. **Dream Mode (nightly skill)**: suggest connections; draft MOCs.
4. **Slow Mode (weekly skill)**: vault health + project briefing.

---

## Governance

- **AUTO**: classify Capture → Brain, standard tags, index compile, link heal, git sync.
- **PROPOSE**: deletes, body edits of human prose, status/deadline changes (use `-- draft.md`).
- **NEVER**: touch secrets, rewrite old git history, or casually mutate `.obsidian/` outside init.

---

## Daily Loop

1. Open `Home.md` or press **Today's Log**.
2. Capture bullets under `## Capture` (`- idea: ...`).
3. Let the Hermes inbox triage cron classify eligible captures; the worker indexes and heals links.
4. Expand promising ideas with `System/skills/idea-expansion.md`.

Chinese README: [README-ZH.md](./README-ZH.md)
