---
type: skill
agent: all
frequency: on-trigger
requires_api: true
tags: [agent, skill, ingestion]
---
# Skill: Source Processing & Ingestion

This skill defines how agents clean up, summarize, and extract knowledge claims from raw web clippings, book excerpts, or transcripts.

## 🎯 Objectives
- Standardize resource formatting and metadata.
- Extract structured summaries and key arguments.
- Connect new clippings to existing projects and areas.

## 📋 Execution Protocol
1.  **Ingestion Trigger**:
    *   Monitor the `Capture/` folder for notes tagged with `#clipping`, `#source`, or containing raw copied articles.
2.  **Processing & Extraction**:
    *   Parse the source content and extract:
        *   Resource Title
        *   Author/Creator
        *   Original URL (if found)
        *   Topics and Tags
    *   Generate a concise, 2-3 sentence executive summary.
    *   Identify 3-5 **Key Claims** (factual or opinionated assertions made in the text).
    *   Rate the **Confidence Level** of the claims from 1 (speculative/low evidence) to 5 (verified/well-supported).
3.  **Template Generation**:
    *   Create a new note in `Brain/` using the `System/templates/source-note.md` structure.
    *   Populate all frontmatter fields (`url`, `author`, `confidence`, `key_claims`, `tags`).
    *   Link the source note to relevant active projects or area notes.
4.  **Cleanup**:
    *   Move the original raw clipping file from `Capture/` into `System/Archive/` to keep the capture inbox clean, or delete it if it is a duplicate.
