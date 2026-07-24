---
type: skill
id: dream-mode
trigger: daily-or-on-demand
automation: observe
safe_to_schedule: true
writes: [System]
tags: [agent, procedure, maintenance, synthesis]
---
# Dream Mode

## Purpose

Surface possible relationships without silently editing the knowledge graph. This procedure may run on a schedule because its output is a review report, not a note mutation.

Read `System/index.json` and recently modified `Brain/` notes. Report:

- likely missing links with evidence from both notes;
- repeated concepts that may justify a MOC;
- contradictions or duplicated claims;
- notes whose provenance or confidence is weak.

Write only a generated report under `System/` or return it directly to the human. Do not add links, rewrite prose, create a MOC, or invoke `fix-links`. Recommendations become changes only after separate human approval.
