---
type: skill
frequency: on-trigger
requires_hermes: false
tags: [agent, procedure, inbox, triage]
---
# Inbox Triage Procedure

Read `System/PROTOCOL.md` first. This is an explicit, user-invoked agent procedure, never a watcher action.

Inspect eligible raw notes directly in `Capture/` and prepare a proposal only. Preserve the body verbatim. For a possible project, use:

```yaml
suggested_type: project
suggested_destination: Active
triage_status: proposed
```

For durable knowledge, propose a title, tags, and links; do not move the note or set `type` unless the user explicitly approves that metadata change. Do not set a project status, priority, deadline, or archive state. Do not delete or call external services.

After the user reviews a project proposal, they complete the project YAML and run `activate --approve`. Finish by running `python3 System/zephyr-worker.py index`.
