---
type: skill
id: source-distillation
trigger: review-queue-or-selection
automation: draft
safe_to_schedule: true
writes: [Capture]
tags: [agent, procedure, capture, distillation]
---
# Source Distillation

## Purpose

Distill a selected clipping, article, transcript, or source note into a traceable knowledge proposal. Preserve the raw source and make uncertainty visible.

## Draft contract

With draft automation enabled, create one collision-safe `<Source> -- distilled -- draft.md` in `Capture/` using `System/templates/source-note.md`. The draft must link to the raw source, record available origin metadata, and distinguish:

- source claims;
- short supporting excerpts;
- the agent’s synthesis;
- confidence and unresolved questions;
- suggested connections.

Do not fabricate an author, URL, publication date, quote, or confidence rationale. Do not delete duplicates or move the source.

## Human gate

The human reviews provenance and prose. Only after approval may the draft become a valid `type: note` and move through `promote --approve --dry-run`, then `promote --approve`.
