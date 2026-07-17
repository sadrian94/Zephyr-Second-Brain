---
type: skill
agent: "{{primary_agent_name}}"
frequency: scheduled
requires_hermes: true
tags: [agent, skill, inbox, triage]
---
# Skill: Hermes Inbox Triage

This routine gives Hermes a bounded, repeatable way to organize raw captures. Hermes provides semantic judgment through its configured provider or OAuth; Zephyr never stores or requests a direct model API key for this task.

## Scope

Only inspect Markdown files directly inside `Capture/` that meet every condition:

- Filename is not `Home.md`.
- Filename does not end with ` -- draft.md`.
- Frontmatter has no `type`.
- Frontmatter does not contain `triage_status: needs_review`.

Do not inspect or modify files outside `Capture/`, `Brain/`, and `System/index.json`.

## Required Classification Contract

For a confidently classified note, preserve the human-authored body verbatim and add or update only frontmatter. The result must use:

```yaml
type: log | note | project
tags: [two-to-four, lowercase-topic-tags]
created: YYYY-MM-DD
```

Use a concise, unique, Windows-safe filename. Never overwrite an existing note to resolve a filename collision.

- `type: log` stays in `Capture/`.
- `type: note` and `type: project` move to `Brain/`.
- Use flat wikilinks only (`[[Note Name]]`) when adding a link is clearly justified.

## Low-Confidence and Safety Rules

If the classification, title, or destination is ambiguous, leave the note in `Capture/` and set:

```yaml
triage_status: needs_review
```

Do not guess. Do not delete files. Do not rewrite, summarize, translate, or otherwise alter the human-authored body. Do not change project status, deadlines, or priorities without following the vault's PROPOSE governance rule.

## Completion

After processing eligible notes, run:

```bash
python3 System/zephyr-worker.py index
```

Final response format:

- No eligible notes: exactly `[SILENT]`
- Otherwise: exactly `Zephyr inbox: processed=<n>, review=<n>, indexed=true`
