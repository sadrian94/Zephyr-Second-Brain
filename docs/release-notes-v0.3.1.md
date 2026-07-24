# Zephyr v0.3.1 Release Notes

## Agent-first operation

- Reframed the documentation around speaking directly with an AI agent. The CLI remains the deterministic implementation layer, not the primary interface for everyday use.
- Added English and Traditional Chinese usage guides with concise conversation patterns for capture, distillation, activation, promotion, review, and maintenance.
- Updated the Codex, Claude, and Gemini adapters to share the same protocol and human-approval boundaries.

## Focused skill set

- Consolidated the bundled procedures into four roles: maintenance, capture triage, source distillation, and review.
- Retired Dream Mode, Slow Mode, idea expansion, inbox triage, and lifestyle reminders from the starter template. Their useful work is now covered by focused capture, distill, review, and explicit human conversation.
- `init-zephyr.py` now installs only the four retained procedures, and its update mode preserves existing personal skill files for manual review.

## Safety and automation

- Kept the local watcher as an optional observe-only convenience: it refreshes generated System evidence and never calls an agent, network service, or modifies notes.
- Capture and distillation remain direct-request or explicit opt-in draft workflows. Activation, promotion, archiving, and prose changes still require current human approval.
