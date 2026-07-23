---
type: skill
tags: [agent, skill, maintenance]
---
# Skill: Dream Mode Maintenance Review

This optional, human-invoked procedure prepares maintenance proposals. It does not designate a permanent agent, run automatically, mutate notes, or contact external services.

## Objectives
- Maintain clean cross-references across all markdown notes in `Brain/`.
- Compile semantic associations and suggest emerging project boundaries.
- Keep the local flat database index synchronized and perform index verification.

## Execution Protocol
1.  **Index Validation**:
    *   Inspect `System/index.json` to verify it matches the files in the directory.
    *   If index inconsistencies are found, trigger the local index compilation.
2.  **Semantic Link Auditing**:
    *   Scan all notes in `Brain/` that have been modified within the last 24 hours.
    *   Compare note text against titles of other notes listed in `System/index.json`.
    *   If a note body contains a reference to another note's title but lacks a `[[Note Name]]` wikilink:
        *   **Propose Link**: Report the recommended link and its evidence for human review.
        *   Do not edit user-authored text.
3.  **Topic Cluster Detection**:
    *   Group notes sharing similar tags or tags matching `#area/...`.
    *   If 3 or more notes share a new unlinked concept, propose a Portal/MOC note (tagged `#moc`) and its suggested filename for human review.
4.  **Reporting**:
    *   Present a local status report to the human detailing:
        *   Number of notes scanned.
        *   Link suggestions generated.
        *   MOC drafts proposed.
