---
type: skill
agent: "{{secondary_agent_name}}"
frequency: weekly
requires_api: false
tags: [agent, skill, maintenance]
---
# Skill: Vault Health & Links Healing

This skill defines the weekly vault health checks and cleanup routines managed by the secondary agent.

## 🎯 Objectives
- Keep internal link structures fully healed and accurate.
- Detect and archive idle or completed items.
- Maintain directory clean-up and remove stray files.

## 📋 Execution Protocol
1.  **Stray Files Audit**:
    *   Ensure all `.md` files (except bootstrap rulebooks and `Home.md` at the root) reside in either `Capture/`, `Brain/`, or `System/`.
    *   If a stray note is found in the root, automatically move it to `Capture/` and flag it for classification.
2.  **Broken Link Resolution**:
    *   Run link healing to detect and match target name case discrepancies.
    *   If a link points to a non-existent note, check `System/index.json` to see if a note with a similar name exists. If so, automatically update the link.
3.  **Archiving Completed Projects**:
    *   Scan projects in `System/index.json` marked as `status: completed` or `status: archived`.
    *   Move the physical files from `Brain/` to `System/Archive/`.
    *   Update `System/index.json` to reflect the new paths.
4.  **Orphan & Attachment Cleanup**:
    *   Scan for orphaned image/media attachments (files in `.obsidian/` or root folders not referenced in any note).
    *   List these orphans in `System/health-status.md` under `## 📎 Unused Attachments` for user review before deletion.
