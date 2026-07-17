# Zephyr Second Brain — Hermes Agent Context

> **Hermes load note:** Hermes injects this file when the session cwd / `TERMINAL_CWD` is the vault root. Only **one** project context source is loaded (`AGENTS.md` wins over `CLAUDE.md` / `.cursorrules`). `GEMINI.md` is for a secondary agent and is **not** auto-loaded by Hermes.
>
> **Identity:** Chat persona may already come from Hermes `SOUL.md`. This file is the **vault operating system** — structure, governance, and workflows. Do not invent a second personality that fights SOUL.md; use placeholders below only when speaking as the vault's primary agent.

## 0. Session Bootstrap (do this first)

1. Treat the vault root as the directory that contains `Capture/`, `Brain/`, and `System/`.
2. Load personal settings from `System/config.json` if present (gitignored). If keys are still placeholders (`<...>`) or missing, fall back to the `{{...}}` tokens below and ask only when a real secret is required.
3. Ensure the context index exists:
   ```bash
   python3 System/zephyr-worker.py index
   ```
   Then read `System/index.json` for notes, tags, links, and `unprocessed_ideas`.
4. Prefer tools over memory for vault state: re-read `System/index.json` after worker runs; do not invent note contents.
5. Design system for dashboards/CSS lives at `System/DESIGN.md` (binding).

### Recommended paths

| Role | Path |
|------|------|
| Template repo (public) | this git checkout — no personal notes |
| Personal vault (default) | `~/Obsidian/Zephyr` after `python3 init-zephyr.py` |

During development, Hermes should usually operate on the **personal vault** cwd, not dump personal notes into the public template.

## 1. Persona & Environment (from config / placeholders)

* **Primary agent name**: `{{primary_agent_name}}`
* **User name**: `{{user_name}}`
* **Preferred language**: `{{preferred_language}}` (chat language; English for code/paths/commands)
* **Timezone**: `{{timezone}}`
* **Secondary agent**: `{{secondary_agent_name}}` (see `GEMINI.md` if that agent is active)

If `System/config.json` exists, its values override unresolved `{{placeholders}}`.

## 2. Core Directives

1. **Unified rules** — follow the rulebook below for folders, frontmatter, links, and governance.
2. **Context index** — use `System/index.json` as the cheap global map; open individual notes only when needed.
3. **Governance** — respect AUTO / PROPOSE / NEVER.
4. **Multi-agent safety** — another agent may share this vault; pull/rebase before coordinated edits on a shared personal vault; never rewrite older git history.
5. **Design compliance** — dashboards/CSS follow `System/DESIGN.md`.
6. **Hermes skills vs vault skills** — Hermes skills live under `~/.hermes/skills/`. Vault routines live under `System/skills/*.md` and are **procedures** to run (cron / on-trigger), not auto-loaded Hermes skills unless you explicitly open them.

## 3. Hermes Tooling Map

| Task | Command / action |
|------|------------------|
| Rebuild index + heal links | `python3 System/zephyr-worker.py index` |
| Triage unclassified inbox | `python3 System/zephyr-worker.py triage` (runs Hermes oneshot or direct LLM API) |
| Explicit git sync | `python3 System/zephyr-worker.py sync` |
| Watch Capture/Brain | `./run-watcher.sh` (or `python3 System/zephyr-watcher.py`) |
| Expand raw ideas | Follow `System/skills/idea-expansion.md` (PROPOSE via `-- draft.md`) |
| Nightly consolidation | `System/skills/dream-mode.md` |
| Weekly briefing | `System/skills/slow-mode.md` |
| Health / archive | `System/skills/vault-maintenance.md` |

Hermes handles model authentication through its configured provider/OAuth or optional custom overrides. Direct LLM API fallback uses credentials configured in `config_local.json`. Routines marked `requires_hermes: true` need a Hermes model session; local index and link-healing commands do not.

---

# Unified Agent Rulebook

## 1. Vault Directory Structure

All notes live in exactly one of:

* `Capture/` — raw ideas, clippings, daily logs, meeting minutes, drafts
* `Brain/` — projects, evergreen notes, areas, portals/MOCs
* `System/` — config, templates, skills, index cache, archive, design

## 2. Note Schema & Metadata

Every note needs frontmatter with `type`:

1. **`project`**: `status` (active/paused/completed/archived), `priority` (high/medium/low), `deadline` (YYYY-MM-DD), `area`
2. **`log`**: `date` (YYYY-MM-DD)
3. **`note`**: evergreen / areas (`#area/...`) / MOCs (`#moc`) + topic `tags`

## 3. Capture-First, Classify-Later

* **Human**: dumps thoughts into `Capture/` or daily log `## Capture` (`- idea: ...`)
* **Hermes**: follows `System/skills/inbox-triage.md` to classify eligible raw captures without rewriting their body text
* **Worker**: `zephyr-worker.py index` compiles metadata and heals links; `sync` is explicit
* **Agent**: cultivates ideas via `System/skills/idea-expansion.md` without destroying raw capture

## 4. Wikilink & Naming

* Wikilinks: flat `[[Note Name]]` only — never folder prefixes
* Filenames: unique, Windows-safe (no `\ / : * ? " < > |`)

## 5. Governance Model

* **AUTO**: Hermes may classify eligible Capture notes → Brain under `inbox-triage.md`; worker may compile `System/index.json` and heal broken/case-mismatched links. Git commit/push is **explicit** and only allowed inside the **personal vault** with an intentionally configured remote.
* **PROPOSE**: deletes, edits to human-written body text, project status/deadline changes — use `* -- draft.md` or ask first.
* **NEVER**: expose secrets/API keys; rewrite git history older than the current session branch; casually edit `.obsidian/` outside `init-zephyr.py`; commit personal notes into the **public template** repo.

## 6. Agent Skills & Automation

* Location: `System/skills/` (`inbox-triage`, `dream-mode`, `slow-mode`, `idea-expansion`, `source-processing`, `vault-maintenance`, `lifestyle-reminders`)
* Frontmatter: `agent`, `frequency` (`nightly` / `weekly` / `on-trigger` / `scheduled`), `requires_hermes`
* Hermes does not loop these continuously in chat — load the skill file and either run the procedure now or configure a Hermes cron job whose `workdir` is the personal vault root.

## 7. Definition of Done (vault tasks)

A vault task is done only when:

1. Required notes exist with valid frontmatter
2. `python3 System/zephyr-worker.py index` succeeds
3. `System/index.json` reflects the change (summaries non-empty for content notes when possible)
4. Governance tier was respected (no silent body rewrites / secret leaks)
