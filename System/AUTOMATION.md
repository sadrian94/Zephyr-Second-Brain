# Zephyr Automation Model v0.3

Automation should reduce clerical friction without hiding commitments. Zephyr therefore grants automation by consequence, not by tool or agent identity.

## Three levels

| Level | May run unattended | May write | Examples |
| --- | --- | --- | --- |
| Observe | Yes | Generated files under `System/` only | validate, index, link report, review queue |
| Draft | Direct human request, or explicit scheduling opt-in | New collision-safe `-- draft.md` notes in `Capture/` | capture triage, source distillation |
| Commit | Never unattended | Approved lifecycle or prose changes | activate, promote, archive, fix links |

Observe automation is deterministic, local, idempotent, and enabled when the watcher is deliberately started. It never invokes an agent or network service.

Draft work has two paths. A direct human request in an agent conversation authorizes one isolated companion draft in `Capture/`; the request is the consent. Scheduled semantic work is disabled by default. To enable scheduling, copy `System/automation.example.json` to `System/automation.json`, set `agent_drafts.enabled` to `true`, and configure the external platform separately. Zephyr core does not schedule or invoke the agent. A scheduled agent must follow the named skill contract, preserve the source, create only a new `-- draft.md` file, refuse collisions, and record its source in proposal frontmatter.

Commit operations always require current human approval. Previous approval for a schedule or draft is not approval to activate, promote, archive, delete, repair links, rewrite prose, or change project status, priority, or deadline.

## Safe refresh

```bash
python3 System/zephyr-worker.py refresh
```

`refresh` validates the vault, rebuilds `System/index.json`, reports links, and writes `System/review-queue.json`. The queue prioritizes invalid notes, overdue or near-term projects, raw captures, daily-log ideas, paused projects, and link issues. It does not change notes.

The optional watcher runs `refresh` after a debounce. Change `on_change` to `index` in `System/automation.json` if only indexing is desired.

## Skill contract

The bundled procedures are `vault-maintenance`, `capture-triage`, `source-distillation`, and `review`. Every procedure declares:

- `id`: stable procedure identifier;
- `trigger`: when a human or scheduler may invoke it;
- `automation`: `observe`, `draft`, or `commit`;
- `safe_to_schedule`: whether unattended invocation is allowed;
- `writes`: permitted output locations.

The most restrictive applicable rule wins. If evidence is incomplete, create a review item or draft; do not guess a commitment.
