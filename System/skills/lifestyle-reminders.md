---
type: skill
id: reminder-brief
trigger: daily-or-on-demand
automation: observe
safe_to_schedule: true
writes: [System]
tags: [agent, procedure, reminders]
---
# Reminder Brief

## Purpose

Prepare a local reminder brief from explicit deadlines and dated logs. Do not infer obligations from casual prose.

Use `System/review-queue.json` and valid dated metadata. A scheduled run may write a generated report under `System/`; it may not change dates, create calendar events, or contact an external service.

External delivery is a separate integration. It requires `external_delivery.enabled: true`, a user-configured destination outside Zephyr core, and platform-specific consent. Never include full private note content when a title, date, and local path are sufficient.
