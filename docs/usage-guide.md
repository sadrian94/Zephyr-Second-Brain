# Zephyr Usage Guide

Zephyr keeps capture easy and commitments visible. Start with raw material; only approve a project, durable note, or archive move when you mean it.

## The daily loop

1. Capture an idea, clipping, or log in `Capture/`. Raw captures may have no frontmatter.
2. Run the safe refresh command:

   ```bash
   python3 System/zephyr-worker.py refresh
   ```

3. Review `System/review-queue.json` or the Home dashboard. It lists raw captures, daily-log ideas, project deadlines, paused work, validation findings, and link issues.
4. Ask an agent to prepare a proposal for a selected item. A proposal is not a commitment.
5. Review the proposal, then use the approved lifecycle command that matches your decision.

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

Agent draft automation is disabled by default. When deliberately enabled, an external agent platform may create one collision-safe companion file ending in `-- draft.md` inside `Capture/`. It must preserve the source and cannot activate, promote, archive, delete, or rewrite anything.

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

Preview, then apply:

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

Preview, then move it to `Brain/`:

```bash
python3 System/zephyr-worker.py promote "Capture/Article clipping -- distilled.md" --approve --dry-run
python3 System/zephyr-worker.py promote "Capture/Article clipping -- distilled.md" --approve
```

## Archive a finished project

First set the project’s status to `completed` or `stopped`. Then preview and apply:

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
