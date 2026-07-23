---
type: skill
frequency: on-trigger
tags: [agent, skill, ingestion]
---
# Skill: Idea Expansion & Deep Ingestion

This user-invoked procedure defines how an agent may prepare an expansion proposal from raw bullet points or ideas. It has no provider-specific dependency.

## Objectives
- Relieve the user of formatting and structuring overhead.
- Transform raw, unstructured thought entries into detailed, actionable project drafts or notes.
- Maintain original entries unchanged to preserve raw intent.

## Execution Protocol
1.  **Idea Discovery**:
    *   Scan notes in `Capture/` lacking standard frontmatter or containing the tag `#idea`.
    *   Scan the `## Capture` section of the current `daily-log.md` for entries starting with `- idea:`.
2.  **Structuring and Expansion**:
    *   Evaluate the raw concept. Determine if it warrants a **Project** (has clear goals and steps) or a **Note/Concept** (is a knowledge item).
    *   **If a Project**:
        *   Formulate a clean, NTFS-safe title.
        *   Flesh out 3-5 initial goals and break them down into actionable steps.
        *   Provide background context based on the raw note content.
        *   Prepare the proposed metadata and outline using `System/templates/project.md` as a reference.
    *   **If a Note**:
        *   Refine the title.
        *   Organize the content into clear, logical headers.
        *   Extract key tags and identify relevant connections.
        *   Prepare the proposed metadata and outline using `System/templates/note.md` as a reference.
3.  **Draft Proposition**:
    *   Present the expanded note, suggested filename (for example `Gmail Smart Router -- draft.md`), and proposed destination for human review.
    *   Do not modify the user's original raw note.
    *   Alert the user: *"I noticed your idea about X and drafted a structured project node at [[Gmail Smart Router -- draft]]. Let me know if you would like me to finalize it!"*
4.  **Finalization**:
    *   Treat any prose or metadata edit, rename, or move as a separate explicit approval. Follow `System/PROTOCOL.md` and use the deterministic worker where applicable.
