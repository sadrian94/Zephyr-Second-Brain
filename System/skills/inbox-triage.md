---
type: skill
id: inbox-triage
trigger: review-queue
automation: draft
safe_to_schedule: true
writes: [Capture]
tags: [agent, procedure, capture, triage]
---
# Inbox Triage

## Purpose

Turn raw captures into reviewable choices without turning them into commitments. Read `System/PROTOCOL.md`, `System/AUTOMATION.md`, and `System/review-queue.json` first.

## Automatic preparation

When `agent_drafts.enabled` is true, an external scheduler may inspect queue items with `action: triage_or_distill`. For each eligible source, it may create at most one collision-safe companion named `<Source> -- draft.md` in `Capture/`. Never modify, rename, tag, or move the source.

The draft must identify its source and remain a proposal:

```yaml
suggested_type: project | note
suggested_destination: Active | Brain
triage_status: proposed
source_note: "[[Original Capture]]"
generated_by: agent
```

Do not invent a project deadline, priority, status, owner, or commitment. If classification is ambiguous, explain both plausible destinations in the draft.

## Human gate

The human may reject the draft, edit it, or approve its metadata. Projects then follow `activate --approve`; durable notes follow `promote --approve` only after the frontmatter is changed to a valid `type: note`. Finish with `refresh`.
