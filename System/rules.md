# Zephyr Second Brain — Unified Agent Rulebook

Canonical Hermes context: **`AGENTS.md`** at the vault root (auto-loaded by Hermes when cwd is the vault).
Secondary agent notes: **`GEMINI.md`** (not auto-loaded by Hermes).

This file is a short mirror for humans browsing `System/`. If it conflicts with `AGENTS.md`, **`AGENTS.md` wins**.

## 1. Vault Directory Structure
* `Capture/` — inbox, daily logs, drafts
* `Brain/` — projects, evergreen, areas, MOCs
* `System/` — config, templates, skills, index, archive, design

## 2. Note Schema
* **project**: status, priority, deadline, area
* **log**: date
* **note**: tags (`#area/...`, `#moc`)

## 3. Capture-First, Classify-Later
Human captures → Hermes runs `System/skills/inbox-triage.md` using its configured provider → `zephyr-worker.py index` compiles metadata and heals links. Agents expand notes via `System/skills/` without destroying raw text.

## 4. Wikilink & Naming
* Flat `[[Note Name]]` only
* NTFS-safe unique filenames

## 5. Governance
* **AUTO**: classify, tag, index, heal links (personal-vault git sync only when intentional)
* **PROPOSE**: deletes, body edits, status/deadline changes (`-- draft.md`)
* **NEVER**: secrets, history rewrite, casual `.obsidian/` edits, personal notes on the public template remote

## 6. Hermes Bootstrap
```bash
python3 System/zephyr-worker.py index
# then read System/index.json
```
Personal vault default: `~/Obsidian/Zephyr` via `python3 init-zephyr.py` (not `--here` during template development).
