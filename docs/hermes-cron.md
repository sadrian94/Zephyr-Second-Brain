# Hermes Cron: Zephyr Inbox Triage

Use this routine after installing a personal Zephyr vault. It uses Hermes's configured provider or OAuth session; do not put model credentials in `System/config.json`.

## Prerequisites

1. Hermes is authenticated in the profile where the job will live.
2. The personal vault has been updated from this template.
3. `python3 System/zephyr-worker.py index` succeeds from the vault root.

## Job settings

Create the job with the Hermes scheduler (Scheduler UI or an agent `cronjob create` action) in the authenticated profile.

| Setting | Value |
|---|---|
| Name | `zephyr-inbox-triage` |
| Schedule | `every 5m` |
| Workdir | Your personal vault root, normally `~/Obsidian/Zephyr` |
| Toolsets | `file`, `terminal` |
| Delivery | `local` |
| Attach to session | `false` |
| Token budget | `700` |
| Turn budget | `6` |
| Time budget | `120` seconds |
| Agent mode | enabled (`no_agent: false`) |

Do not attach a `System/skills/` file as a Hermes global skill. These vault-local routines are not auto-loaded; the prompt below explicitly requires the job to read the protocol file.

## Prompt

```text
You are the Zephyr inbox triage worker.

Work only inside the current vault workdir. First read AGENTS.md and
System/skills/inbox-triage.md. Follow that protocol exactly.

Process only eligible unclassified Markdown notes in Capture/. Do not use or
request a direct LLM API key. Do not modify existing human-authored body text.
For low confidence, leave the note in Capture/ with
triage_status: needs_review instead of guessing.

After any processing, run:
python3 System/zephyr-worker.py index

If nothing was eligible, output exactly [SILENT]. Otherwise output exactly:
Zephyr inbox: processed=<n>, review=<n>, indexed=true
```

## Model selection and token control

Start with the authenticated profile's default model. After a successful manual run, pin a lower-cost model only after confirming its exact provider/model ID is available to that OAuth account. A model override belongs on the cron job, not in Zephyr's config.

Keep the job narrow: the protocol, `file` + `terminal` toolsets, token budget, turn budget, and short output format matter more than choosing a model by name. OAuth plans may still impose model availability, usage, or rate limits.

## Verification

1. Add one short unclassified Markdown note to `Capture/`.
2. Manually run the new job once.
3. Confirm the note body is unchanged, the frontmatter follows `inbox-triage.md`, and `System/index.json` includes the result.
4. Add an ambiguous note and confirm it remains in `Capture/` with `triage_status: needs_review`.
5. Re-run the job; confirm that reviewed note is skipped and an empty run returns `[SILENT]`.

Do not enable a Hermes-triggering watcher while this cron is the primary inbox processor. The built-in watcher only rebuilds the deterministic index.
