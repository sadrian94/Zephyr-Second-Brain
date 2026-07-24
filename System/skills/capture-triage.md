---
type: skill
id: capture-triage
trigger: direct-conversation-or-review-queue
automation: draft
safe_to_schedule: true
writes: [Capture]
tags: [agent, procedure, capture, triage, ideation]
---
# Capture Triage

## Purpose

Turn a raw capture or daily-log idea into a clear, reviewable choice. It combines classification with light idea expansion: enough structure to decide what the item is, never enough invention to turn it into an unchosen commitment.

## Direct conversation

When the human directly asks to capture, triage, or expand a named item, that request authorizes one new collision-safe raw note or `-- draft.md` companion in `Capture/`. This is a one-item authorization, not standing authority over future captures.

Preserve the source. Record `triage_status: proposed`, `generated_by: agent`, and a wikilink to the source. State:

- facts present in the source;
- inferences and open questions;
- a concise concept or problem statement;
- candidate links and tags;
- whether it resembles a project proposal or durable knowledge;
- 3–5 possible next steps or lines of inquiry, where useful.

For scheduled work, `agent_drafts.enabled` must be true. A scheduler may create at most one collision-safe `<Source> -- draft.md` for each eligible queue item.

## Boundaries

Do not modify, rename, tag, or move the source. Do not invent a deadline, priority, status, owner, or task commitment. The human reviews the draft before a project can use `activate --approve` or a durable note can use `promote --approve`.
