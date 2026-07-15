---
type: skill
agent: "{{primary_agent_name}}"
frequency: weekly
requires_api: true
tags: [agent, skill, reporting]
---
# Skill: Slow Mode Weekly Routine

This skill defines the strategic weekly reviews and briefings performed by the primary agent every Monday morning.

## 🎯 Objectives
- Provide a high-level executive summary of project progress, upcoming deadlines, and task velocities.
- Audit vault health and list orphaned items.
- Update lifestyle schedules and coordinate notifications.

## 📋 Execution Protocol
1.  **Weekly Briefing Generation**:
    *   Scan all active projects in `System/index.json` (`status: active`).
    *   Examine deadlines and calculate days remaining:
        *   Flag any projects with deadlines within 7 days as `[🔥 HIGH RISK]`.
        *   Flag overdue projects as `[⚠️ OVERDUE]`.
    *   Scan daily logs from the past week (`Capture/*.md` with `type: log`) to compile completed tasks (wins).
    *   Format a clean markdown report containing:
        *   **Weekly Highlights**: Key tasks completed.
        *   **Project Health Grid**: Status, priority, and upcoming milestones of active projects.
        *   **Risk Alerts**: List of close or overdue deadlines.
2.  **Vault Health Summary**:
    *   Identify "orphan notes" (any notes in `Brain/` with zero incoming backlinks).
    *   List broken wikilinks (links pointing to notes that do not exist).
    *   Save these findings in `System/health-status.md`.
3.  **Discord Delivery**:
    *   Send the formatted briefing directly to the Discord webhook configured in `System/config.json`.
    *   Keep the briefing tone polite, concise, and structured.
