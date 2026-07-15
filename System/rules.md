# Zephyr Second Brain — Unified Agent Rulebook

Welcome to **Zephyr**, a lightweight, invisible second brain built for cross-device sync and multi-agent collaboration.

## 1. Vault Directory Structure
All notes in the vault reside in exactly one of three folders:
*   `Capture/`: Where the user captures raw ideas, clippings, daily logs, and meeting minutes.
*   `Brain/`: The flat pool of all active projects, areas, portals, and evergreen notes.
*   `System/`: Vault-level configurations, templates, skills, indexing cache, and archived notes.

## 2. Note Schema & Metadata
Every note MUST maintain a minimal frontmatter block identifying its `type`:
1.  **`project`**: Active endeavors. Fields: `status` (active/paused/completed/archived), `priority` (high/medium/low), `deadline` (YYYY-MM-DD), `area`.
2.  **`log`**: Daily notes, meetings, logs. Fields: `date` (YYYY-MM-DD).
3.  **`note`**: Evergreen knowledge, areas (tagged `#area/...`), and portals/MOCs (tagged `#moc`). Fields: `tags` (topic tags).

## 3. Capture-First, Classify-Later
*   **Human Role**: Captures freeform thoughts, logs, and ideas inside `Capture/` or daily logs.
*   **Worker Role**: Local script (`zephyr-worker.py`) watches `Capture/`, auto-classifies notes, formats headers, and moves knowledge notes/projects to `Brain/`.
*   **Agent Role**: AI Agents scan ideas in `Capture/` and actively guide the user to cultivate/expand them into structured projects or notes (refer to `System/skills/idea-expansion.md`).

## 4. Wikilink & Naming Conventions
*   **Wikilinks**: Always use plain flat wikilinks: `[[Note Name]]`. Never include folder prefixes.
*   **Filenames**: Keep filenames unique and Windows NTFS safe (no `\ / : * ? " < > |` characters).

## 5. Governance Model
*   **AUTO**: Auto-classify captured notes from `Capture/` to `Brain/`, add standard tags, compile `System/index.json`, and fix broken internal links. Git pull/commit/push.
*   **PROPOSE**: Deleting files, modifying user-written note bodies, or altering project statuses/deadlines.
*   **NEVER**: Modifying `.obsidian/` files, exposing secrets, or altering git commits older than the current session branch.

## 6. Agent Skills & Automation
*   **Skills Location**: All agent skills are stored as markdown files under `System/skills/` (e.g., `System/skills/dream-mode.md`, `System/skills/slow-mode.md`).
*   **Skill Metadata**: Each skill contains frontmatter with metadata like `agent`, `frequency` (e.g., `nightly`, `weekly`, `scheduled`, `on-trigger`), and `requires_api`.
*   **Cron Jobs & Scheduling**: The core automation skills (e.g., `dream-mode`, `slow-mode`, `lifestyle-reminders`) define routine procedures. AI agents (like Hermes-agent) do not run these continuously in chat; instead, they read these files to establish and configure background cron jobs or scheduled execution triggers on the hosting system.

