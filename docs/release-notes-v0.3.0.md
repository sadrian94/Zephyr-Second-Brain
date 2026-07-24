# Zephyr v0.3.0 Release Notes

## Consequence-based automation

- Added a three-level automation model: unattended observation, opt-in companion drafts, and human-approved commits.
- Added `refresh`, which validates, indexes, reports links, and creates `System/review-queue.json` without editing notes.
- Updated the optional watcher to run `refresh` by default; it still never invokes an agent or network service.

## Capture and distillation

- Standardized all seven bundled skills with stable IDs, triggers, automation levels, scheduling safety, and allowed write locations.
- Added queue-driven triage, idea expansion, and source distillation contracts. Opted-in agents may create only separate collision-safe drafts in `Capture/` and must preserve source material.
- Added `promote --approve` so reviewed durable notes and distillations have a deterministic path from `Capture/` to `Brain/`.

## Review and governance

- Review queue signals include invalid notes, raw captures, daily-log ideas, overdue and near-term projects, paused projects, and link issues.
- Dream Mode, weekly review, reminders, and maintenance can be scheduled only as observe-level reports.
- Activation, promotion, archiving, link repair, prose edits, deletion, status, priority, and deadline changes remain human-gated.
