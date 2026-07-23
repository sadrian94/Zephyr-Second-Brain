# Zephyr v0.2.1 Release Notes

## Agent-neutral coordination

- Removed permanent primary and secondary agent roles from the core configuration and installer prompts.
- Added a canonical one-writer rule: one active operator may mutate a vault during a task or session; reviewers and specialists are read-only by default.
- Added a thin `CLAUDE.md` adapter and refreshed the Codex and Gemini adapters to point to the same canonical protocol.

## Compatibility and safety

- Existing `System/config.json` files keep unknown and legacy agent-name fields unchanged; Zephyr now ignores them.
- `init-zephyr.py --update` refreshes root agent adapters without overwriting personal configuration or notes.
- Bundled agent procedures no longer require Hermes or provider-specific behavior, and Dream Mode now produces reviewable proposals rather than automatic edits or external notifications.

## Verification

- Added installer and adapter regression coverage for the agent-neutral model.
- Deterministic validation, indexing, activation, archive, and watcher behavior are unchanged.
