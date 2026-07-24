# Zephyr Usage Guide

Zephyr keeps capture easy and commitments visible. Talk to an AI agent for ordinary work; the CLI is the auditable transaction layer that the agent or you use after an explicit decision.

## Agent-first operating model

You can say:

```text
Capture this idea: I want to compare local language models for private research.
```

```text
Distill Capture/Article clipping.md. Preserve the source and show me a draft.
```

```text
What in Zephyr needs my decision this week?
```

```text
I approve the Local model research proposal as a project. Preview the move, then apply it.
```

A direct request authorizes one new raw Capture or companion draft only. The agent may refresh generated state and explain its proposal, but it cannot turn that draft into an active project, a Brain note, an archive record, or a prose rewrite without a new explicit approval.

## The daily loop

1. Ask the agent to capture an idea, clipping, or log in `Capture/`. Raw captures may have no frontmatter.
2. The agent runs the safe refresh command:

   ```bash
   python3 System/zephyr-worker.py refresh
   ```

3. Review `System/review-queue.json` or the Home dashboard. It lists raw captures, daily-log ideas, project deadlines, paused work, validation findings, and link issues.
4. Ask the agent to prepare a proposal for a selected item. A proposal is not a commitment.
5. Review the proposal and give explicit approval when you want a lifecycle command applied.

## Capture

Use the Quick Capture form in `Capture/Capture.md`, create a Markdown file directly in `Capture/`, or use a daily log. Keep the first note short; completeness can come later.

Examples of useful agent requests:

```text
Triage Capture/Local models.md. Preserve the source and prepare a proposal only.
```

```text
Distill Capture/Article clipping.md. Separate source claims, excerpts, synthesis, confidence, and open questions.
```

```text
Expand this daily-log idea. State assumptions and possible next steps, but do not create a deadline or commitment.
```

## Review and draft automation

The local `refresh` command is safe to run unattended: it writes generated data under `System/` only. It never invokes an agent or edits notes.

Direct conversation does not need persistent draft automation: your request authorizes one collision-safe companion file ending in `-- draft.md` inside `Capture/`. It must preserve the source and cannot activate, promote, archive, delete, or rewrite anything.

Scheduled agent draft automation is disabled by default. When deliberately enabled, an external agent platform may create the same kind of companion draft without a live conversation.

To opt in, copy `System/automation.example.json` to `System/automation.json`, set `agent_drafts.enabled` to `true`, and configure the external agent scheduler separately. See [the automation model](../System/AUTOMATION.md).

## Activate a project

After review, replace proposal frontmatter with a complete project record:

```yaml
---
type: project
status: active
priority: medium
deadline: 2026-08-31
area: "[[Research]]"
tags: [project]
---
```

Tell the agent, “I approve this as a project. Preview, then apply.” It should run:

```bash
python3 System/zephyr-worker.py activate "Capture/Local model research.md" --approve --dry-run
python3 System/zephyr-worker.py activate "Capture/Local model research.md" --approve
```

The project moves to `Active/`. The dry run changes nothing and should be the default first step.

## Promote a durable or distilled note

Review the draft, then convert its frontmatter to a valid note:

```yaml
---
type: note
tags: [source, local-ai]
source_note: "[[Article clipping]]"
---
```

Tell the agent, “I approve this note for Brain. Preview, then apply.” It should run:

```bash
python3 System/zephyr-worker.py promote "Capture/Article clipping -- distilled.md" --approve --dry-run
python3 System/zephyr-worker.py promote "Capture/Article clipping -- distilled.md" --approve
```

## Archive a finished project

First explicitly approve the status change to `completed` or `stopped`. Then tell the agent to preview and archive:

```bash
python3 System/zephyr-worker.py archive "Active/Local model research.md" --approve --dry-run
python3 System/zephyr-worker.py archive "Active/Local model research.md" --approve
```

## Maintenance and troubleshooting

| Need | Command | Changes notes? |
| --- | --- | --- |
| Refresh safe generated state | `python3 System/zephyr-worker.py refresh` | No |
| Check frontmatter and names | `python3 System/zephyr-worker.py validate` | No |
| Strict health check | `python3 System/zephyr-worker.py health` | No |
| Preview case-only link repair | `python3 System/zephyr-worker.py fix-links --approve --dry-run` | No |
| Apply reviewed case-only link repairs | `python3 System/zephyr-worker.py fix-links --approve` | Yes |

The optional watcher runs `refresh` after local Markdown changes. Start it with `run-watcher.bat` on Windows or `./run-watcher.sh` on macOS/Linux. It remains local-only.

For the full authority model, read [System/PROTOCOL.md](../System/PROTOCOL.md).
