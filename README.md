# Zephyr Second Brain

> Named after **Zephyrus**, the Greek god of the West Wind. Zephyr is a lightweight, flow-first Obsidian second brain for humans + Hermes-agent.

Deep dives:
- [Philosophy & Positioning](./docs/philosophy-and-positioning.md)
- [Architecture](./docs/architecture.md)
- [Project Management](./docs/project-management.md)

Zephyr keeps you in capture flow. Local workers and agents handle classification, linking, indexing, and maintenance.

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

### Option B — Use this repo as the vault (`--here`)

Only if you intentionally want the template checkout itself to act as the vault:

```bash
python3 init-zephyr.py --here
python3 System/zephyr-worker.py index
./run-watcher.sh
```

`--here` writes gitignored `System/config.json` only; it does **not** rewrite tracked `AGENTS.md` / `GEMINI.md` with personal names.

### Optional: AI classification

In the **personal vault**, edit `System/config.json` (created by init) and set a real `ai_api_key`.
Or copy from the template: `System/config.example.json` → personal vault `System/config.json`.
Without a key, the worker still indexes, heals links, and uses offline heuristics.

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
   - Classifies unclassified notes (LLM or offline fallback)
   - Compiles `System/index.json`
   - Heals case-mismatched wikilinks
   - Optional git auto-commit / pull --rebase / push
2. **Dream Mode (nightly skill)**: suggest connections; draft MOCs.
3. **Slow Mode (weekly skill)**: vault health + project briefing.

---

## Governance

- **AUTO**: classify Capture → Brain, standard tags, index compile, link heal, git sync.
- **PROPOSE**: deletes, body edits of human prose, status/deadline changes (use `-- draft.md`).
- **NEVER**: touch secrets, rewrite old git history, or casually mutate `.obsidian/` outside init.

---

## Daily Loop

1. Open `Home.md` or press **Today's Log**.
2. Capture bullets under `## Capture` (`- idea: ...`).
3. Let the watcher/worker classify and index.
4. Expand promising ideas with `System/skills/idea-expansion.md`.

Chinese README: [README-ZH.md](./README-ZH.md)
