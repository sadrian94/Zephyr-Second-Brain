---
type: skill
id: review
trigger: weekly-daily-or-on-demand
automation: observe
safe_to_schedule: true
writes: [System]
tags: [agent, procedure, review, synthesis]
---
# Review

## Purpose

Prepare one calm decision brief from the evidence already in the vault. This combines operational weekly review with knowledge-graph review so the human receives one coherent ledger rather than competing reports.

Read `System/review-queue.json`, `System/index.json`, recent logs, Active project metadata, and recently modified Brain notes. Report only evidence-backed observations:

- overdue or near-term commitments, paused work, and unresolved captures;
- recent wins or recurring friction explicitly recorded in logs;
- likely missing links, repeated concepts, contradictions, or weak provenance;
- choices that require the human’s attention and items safe to defer.

Write a generated report under `System/` or return it directly to the human. Do not add links, create a MOC, change project fields, schedule work, send notifications, or archive material. Recommendations become changes only after separate human approval.
