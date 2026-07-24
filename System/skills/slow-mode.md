---
type: skill
id: weekly-review
trigger: weekly-or-on-demand
automation: observe
safe_to_schedule: true
writes: [System]
tags: [agent, procedure, review, reflection]
---
# Weekly Review

## Purpose

Prepare a calm decision brief from current evidence; do not manufacture urgency.

Use `System/review-queue.json`, `System/index.json`, recent logs, and Active project metadata. Summarize:

- overdue and near-term commitments;
- paused work and unresolved captures;
- recent wins or recurring friction explicitly present in logs;
- choices that require the human’s attention;
- items safe to ignore until the next review.

Write only a generated report under `System/` or return it directly. Do not change project fields, schedule work, send notifications, or archive anything.
