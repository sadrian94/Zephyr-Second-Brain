---
type: skill
agent: all
frequency: on-trigger
requires_api: true
tags: [agent, skill, ingestion]
---
# Skill: Idea Expansion & Deep Ingestion

This skill defines how agents process and expand raw bullet points or ideas into structured knowledge components.

## 🎯 Objectives
- Relieve the user of formatting and structuring overhead.
- Transform raw, unstructured thought entries into detailed, actionable project drafts or notes.
- Maintain original entries unchanged to preserve raw intent.

## 📋 Execution Protocol
1.  **Idea Discovery**:
    *   Scan notes in `Capture/` lacking standard frontmatter or containing the tag `#idea`.
    *   Scan the `## 📥 Capture` section of the current `daily-log.md` for entries starting with `- idea:` or `- 💡`.
2.  **Structuring and Expansion**:
    *   Evaluate the raw concept. Determine if it warrants a **Project** (has clear goals and steps) or a **Note/Concept** (is a knowledge item).
    *   **If a Project**:
        *   Formulate a clean, NTFS-safe title.
        *   Flesh out 3-5 initial goals and break them down into actionable steps.
        *   Provide background context based on the raw note content.
        *   Populate the `System/templates/project.md` structure.
    *   **If a Note**:
        *   Refine the title.
        *   Organize the content into clear, logical headers.
        *   Extract key tags and identify relevant connections.
        *   Populate the `System/templates/note.md` structure.
3.  **Draft Proposition**:
    *   Write the expanded note into `Capture/` with the filename suffix `-- draft.md` (e.g. `Gmail Smart Router -- draft.md`).
    *   Do not modify the user's original raw note.
    *   Alert the user: *"I noticed your idea about X and drafted a structured project node at [[Gmail Smart Router -- draft]]. Let me know if you would like me to finalize it!"*
4.  **Finalization**:
    *   Upon user approval, remove the `-- draft` suffix, update its frontmatter metadata, and move it to `Brain/`.
