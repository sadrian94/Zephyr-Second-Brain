---
type: skill
id: idea-expansion
trigger: review-queue
automation: draft
safe_to_schedule: true
writes: [Capture]
tags: [agent, procedure, capture, ideation]
---
# Idea Expansion

## Purpose

Give a raw idea enough structure to evaluate it while preserving the original thought and uncertainty.

## Inputs

- `idea` items in `System/review-queue.json`;
- raw Capture notes explicitly selected by the human;
- the matching source content and nearby context only.

## Draft contract

With draft automation enabled, create one new collision-safe `<Idea> -- draft.md` in `Capture/`. Record `triage_status: proposed`, `generated_by: agent`, and a wikilink to the source. Never append to the daily log or replace the source note.

Separate facts found in the source from inference and open questions. Propose:

- a concise problem or concept statement;
- why it may matter;
- 3–5 possible next steps or lines of inquiry;
- candidate links and tags;
- whether it resembles a durable note or a project proposal.

Do not create a deadline, priority, status, or task commitment. Human approval is required before any rename, metadata conversion, promotion, or activation.
