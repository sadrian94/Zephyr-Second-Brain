---
type: skill
agent: "{{primary_agent_name}}"
frequency: nightly
requires_api: true
tags: [agent, skill, maintenance]
---
# Skill: Dream Mode Nightly Routine

This skill defines the nightly routine executed by the primary agent to consolidate knowledge, optimize link relationships, and heal metadata.

## 🎯 Objectives
- Maintain clean cross-references across all markdown notes in `Brain/`.
- Compile semantic associations and suggest emerging project boundaries.
- Keep the local flat database index synchronized and perform index verification.

## 📋 Execution Protocol
1.  **Index Validation**:
    *   Inspect `System/index.json` to verify it matches the files in the directory.
    *   If index inconsistencies are found, trigger the local index compilation.
2.  **Semantic Link Auditing**:
    *   Scan all notes in `Brain/` that have been modified within the last 24 hours.
    *   Compare note text against titles of other notes listed in `System/index.json`.
    *   If a note body contains a reference to another note's title but lacks a `[[Note Name]]` wikilink:
        *   **Propose Link**: Append a recommended link section at the bottom under a `## 🔗 Suggested Connections` header.
        *   Do not overwrite existing user-authored text.
3.  **Topic Cluster Detection**:
    *   Group notes sharing similar tags or tags matching `#area/...`.
    *   If 3 or more notes share a new unlinked concept, draft a proposed Portal/MOC note (tagged `#moc`) inside `Capture/` with the filename `MOC - <Concept Name> -- draft.md`.
4.  **Reporting**:
    *   Post a silent nightly status update to the configured Discord channel detailing:
        *   Number of notes scanned.
        *   Link suggestions generated.
        *   MOC drafts proposed.
