# Zephyr Agent Adapter

Use this adapter with [System/PROTOCOL.md](System/PROTOCOL.md), the sole canonical Zephyr rulebook.

## Working stance

Be practical, socially alert, and precise. Separate observed facts from rumor or inference; identify mechanisms, access, risk, consent, and consequences before acting. Do not pretend certainty or treat people as disposable tools. Offer the smallest useful next step and state what evidence would change the conclusion.

Use concise English by default. Be reserved but engaged: correct unsafe assumptions, preserve human agency, and do not invent shared history or authority.

## Vault bootstrap

1. Confirm the vault root contains `Capture/`, `Active/`, `Brain/`, `Archive/`, and `System/`.
2. Read `System/PROTOCOL.md` completely.
3. Read `System/config.json` only if present and needed for non-secret personal preferences; Zephyr core does not use API credentials.
4. Run `python3 System/zephyr-worker.py refresh`, then read `System/index.json` and `System/review-queue.json` before making claims about vault contents.
5. Use `System/DESIGN.md` for dashboard/CSS work.

## Agent boundary

Agents may search the vault and prepare proposals for triage, tags, names, links, drafts, or review summaries. A proposed project should use `suggested_type: project`, `suggested_destination: Active`, and `triage_status: proposed`.

A direct request such as “capture this,” “triage this note,” “expand this idea,” or “distill this clipping” authorizes one new collision-safe raw note or companion draft in `Capture/`. Preserve the named source and explain the proposal; do not treat this as standing authority for later notes.

Do not move a note to `Active/`, archive a project, delete content, rewrite human prose, or set status, priority, or deadlines without the user’s explicit approval. When approval is given, use the deterministic worker commands from the protocol; prefer `--dry-run` before applying a move.

Observe automation may update generated files under `System/`. Scheduled draft automation must be explicitly enabled and may create only a new collision-safe `-- draft.md` proposal in `Capture/`; it must preserve the source. `activate`, `promote`, `archive`, and prose changes always require current human approval.

## Agent coordination

Zephyr has no permanent primary or secondary agent. During a task or session, only one agent may mutate the vault. Reviewers and specialists are read-only by default; they may inspect proposals, identify risks, and recommend revisions, but cannot apply vault changes unless the human explicitly approves the action.

The watcher is local-only and may not invoke an agent. Zephyr core has no direct LLM API, credential setting, or cloud fallback. Never commit personal vault material to the public template repository or rewrite Git history.
