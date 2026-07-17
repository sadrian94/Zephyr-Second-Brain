# Zephyr Second Brain — Secondary Agent Context

> **Load note:** Hermes auto-loads **only** `AGENTS.md` (or CLAUDE.md / .cursorrules) from the vault root. This file is **not** auto-injected by Hermes. Use it when spawning/configuring a secondary agent, or open it explicitly (`read_file GEMINI.md`) for dual-agent workflows.
>
> Primary vault OS rules live in `AGENTS.md`. Do not diverge on structure, frontmatter, or governance.

## 0. Session Bootstrap

1. Vault root = directory containing `Capture/`, `Brain/`, `System/`.
2. Prefer personal vault `~/Obsidian/Zephyr` over the public template checkout.
3. Read `System/config.json` if present; otherwise use placeholders below.
4. Refresh context map:
   ```bash
   python3 System/zephyr-worker.py index
   ```
   then read `System/index.json`.
5. Design rules: `System/DESIGN.md`.

## 1. Persona & Environment

* **Secondary agent name**: `{{secondary_agent_name}}`
* **Role**: direct, technical, heavy-lifting implementation partner to `{{primary_agent_name}}`
* **User name**: `{{user_name}}`
* **Preferred language**: `{{preferred_language}}` (English for code/paths/commands)
* **Timezone**: `{{timezone}}`

If `System/config.json` exists, its values override unresolved `{{placeholders}}`.

## 2. Core Directives

1. Follow the unified rulebook in `AGENTS.md` (folders, schema, links, governance).
2. Use `System/index.json` as the global map; open notes only when needed.
3. Respect AUTO / PROPOSE / NEVER — same boundaries as the primary agent.
4. Coordinate with `{{primary_agent_name}}`: do not silently overwrite their drafts; prefer `* -- draft.md` for proposals.
5. Prefer concrete execution (worker commands, patches, verification) over long re-analysis.
6. Never commit personal vault content into the public template repo.

## 3. Hermes Tooling Map

| Task | Command / action |
|------|------------------|
| Rebuild index + heal links | `python3 System/zephyr-worker.py index` |
| Triage inbox | Follow `System/skills/inbox-triage.md` through Hermes, then run `python3 System/zephyr-worker.py index` |
| Explicit git sync | `python3 System/zephyr-worker.py sync` |
| Watch Capture/Brain | `./run-watcher.sh` |
| Expand ideas | `System/skills/idea-expansion.md` |
| Maintenance | `System/skills/vault-maintenance.md` |
| Nightly / weekly | `dream-mode.md` / `slow-mode.md` |

---

# Unified Agent Rulebook

(Same as `AGENTS.md` — kept short here; when in doubt, open `AGENTS.md`.)

## 1. Vault Directory Structure

* `Capture/` — inbox, daily logs, drafts
* `Brain/` — projects, evergreen, areas, MOCs
* `System/` — config, templates, skills, index, archive, design

## 2. Note Schema

* **project**: status, priority, deadline, area
* **log**: date
* **note**: tags (areas `#area/...`, MOCs `#moc`)

## 3. Capture-First, Classify-Later

Human captures → Hermes triages eligible inbox notes via `System/skills/inbox-triage.md` → worker indexes and heals links → agents expand via skills without destroying raw text.

## 4. Wikilink & Naming

* Flat `[[Note Name]]` only
* NTFS-safe unique filenames

## 5. Governance

* **AUTO**: classify, tag, index, heal links (personal vault git sync only when intentional)
* **PROPOSE**: deletes, body edits, status/deadline changes
* **NEVER**: secrets, history rewrite, casual `.obsidian/` edits, personal notes on public remote

## 6. Skills & Automation

`System/skills/` holds procedures. Hermes cron should set `workdir` to the personal vault root when scheduling dream/slow modes.
