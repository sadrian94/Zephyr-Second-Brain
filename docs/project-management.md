# Zephyr Project Management Guide

This document introduces how to manage personal projects using the "Flow-First" model in the Zephyr system. This design aims to eliminate the maintenance fatigue and complex grid clutter common in traditional tools (e.g., Jira, Notion), detailing how **Hermes-agent** and the local engine work behind the scenes.

---

## 1. Core Design Philosophy

Project management in Zephyr is built on three main principles:
* **Flow Over Friction**: We reject micro-level hour logging or complex task drag-and-drop actions. A project file is simply a standard Markdown document, and tasks are represented by native checklist markers `[ ]`.
* **Zero Active Vault Clutter**: The `Brain/` folder only displays active, immediate priorities. All completed or paused projects are automatically removed from the active directory to free up mental focus.
* **Agent-Led Warnings & Drafting**: The most tedious tasks—such as creating task breakdowns, tracking due dates, and auditing project health—are fully delegated to **Hermes-agent** in the background.

---

## 2. Project Metadata Schema

Every project file must begin with the following YAML frontmatter attributes:

```yaml
---
type: project
status: active      # active | paused | completed | archived
priority: medium    # high | medium | low
deadline: 2026-08-30 # Must use YYYY-MM-DD format
area: tech-dev      # Area of knowledge it maps to (e.g., tech-dev, finance, lifestyle)
---
```

### Standard Project Template (`System/templates/project.md`)
```markdown
# Project Name

> [!NOTE]
> Brief description of project background and core goals.

## 🎯 Milestones
- [ ] Milestone A
- [ ] Milestone B

## 📋 Task List
- [ ] Task 1
- [ ] Task 2

## 🔗 Related Resources & Evergreen Notes
- [[Related-Note-A]]
- [[Related-Note-B]]
```

---

## 3. Project Lifecycle Walkthrough

In Zephyr, a project moves smoothly through five distinct phases:

### 3.1 Phase 1: Capture
* **Human Action**: You jot down a raw idea in the `## Ingestion` section of your Daily Log (`Capture/2026-07-15.md`):
  ```markdown
  - 💡 Create a smart email router to automatically classify customer support emails.
  ```
* **System State**: Your flow remains unbroken; you continue with your active writing.

### 3.2 Phase 2: Proposal
* **System & AI Action**:
  1. **Detection & Flagging**: When you save your Daily Log, the local `zephyr-worker.py` scans the new idea. Seeing that it lacks a WikiLink, it registers the idea's metadata (source path, line number, text) in **`unprocessed_ideas` inside `System/index.json`**.
  2. **Hermes-Agent Run**: Upon activation (via scheduler or direct call), Hermes-agent reads the unprocessed list from `index.json` and loads **`System/skills/idea-expansion.md`** as its execution SOP.
  3. **Drafting & Backlinking**: The agent breaks down tasks, creates the draft at `Capture/email-router--draft.md`, and updates your Daily Log line to append the backlink: `- 💡 Create a smart email router... (Draft: [[email-router--draft]])`.
* **System State**: AI sends a light notification: *"I noticed your idea about an email router and drafted a project node at [[email-router--draft]]"*. On the next worker run, the processed idea is automatically cleared from the `unprocessed_ideas` list as it now contains a WikiLink.

### 3.3 Phase 3: Activation
* **Human Action**:
  1. You open `[[email-router -- draft]]` and review the AI-suggested milestones.
  2. You edit or add custom tasks.
  3. **One-Click Activation**: You rename the file to `email-router` (removing the `-- draft` suffix) and ensure `status` is set to `active`.
* **System Action (Local Python Worker)**:
  The Python daemon detects the filename change and active status, and **moves the file physically from `Capture/` to the Brain folder at `Brain/email-router.md`**.
* **System State**: The project immediately appears in the **Active Projects** grid on your `Home.md` and `Brain.md` dashboards.

### 3.4 Phase 4: Execution & Audit
* **Human Action**: You check off completed tasks by editing `[ ]` to `[x]` inside the file.
* **AI Action (Slow Mode Weekly Audit)**:
  Every Monday morning, Hermes-agent scans the `index.json` to perform audit calculations:
  * **Risk Auditing**: Compares the current date with the project `deadline`. If the deadline is within 7 days, it flags it as `[🔥 HIGH RISK]`; if overdue, it flags it as `[⚠️ OVERDUE]`.
  * **Highlights Aggregation**: Scans the past week's Daily Logs for completed wins linked to this project.
  * **Delivery**: Posts the weekly status grid report directly to your Discord channel.

### 3.5 Phase 5: Automatic Archiving
* **Human Action**: When the project is finished, you change the metadata status to:
  ```yaml
  status: completed
  ```
* **System Action (Local Python Worker)**:
  The daemon detects the completed status in seconds and **physically moves the file to the archive directory: `System/Archive/email-router.md`**.
* **System State**: The project disappears from your active dashboards, eliminating visual noise, while remaining fully retrievable in your archive index.

---

## 4. Why This System Fits You

| Attribute | Traditional SaaS (Jira, Notion) | Zephyr Project Management |
| :--- | :--- | :--- |
| **Creation Effort** | High (Manually create file, select templates, configure folders and fields) | Near Zero (Jot down a quick bullet; AI drafts the structure) |
| **Maintenance Burden** | High (Manually drag cards, clean completed tasks, relocate files) | Zero (Relies on background daemon to auto-archive completed projects) |
| **Visual Clutter** | High (Rounded cards, decorative emojis, heavy shadows) | Near Zero (Warm Monochrome layout showing only essential deadlines) |
| **Task Tracking** | Passive (Requires you to open the tool and actively review statuses) | Active (AI updates project risks and pushes reports directly to your Discord) |
