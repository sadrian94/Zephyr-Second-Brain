# Zephyr Second Brain — Design System & Guidelines

This document outlines the core design preferences, patterns, and styling rules established for the **Zephyr Second Brain**. It serves as a source of truth for maintainers, human developers, and AI agents to ensure design consistency across all dashboards and note layouts.

---

## 1. Design Aesthetics & Philosophy
Zephyr follows a **Utilitarian Editorial Minimalism** aesthetic. 
- **Purpose-Driven Visuals**: Color, borders, and animations are treated as scarce resources used exclusively to establish hierarchy, show status, or guide interaction.
- **Strict Anti-Slop Guidelines**: Avoid generic SaaS design patterns (such as heavy drop shadows, rounded pill buttons, saturated gradients, or decorative emoji clutter). 

---

## 2. Color Palette (Warm Monochrome + Spot Pastels)

Color values adjust automatically to support both **Light/Warm Mode** and **Dark Mode** layouts through semantic custom properties:

| Color Role | Light/Warm Mode Value | Dark Mode Value | Style Target |
| :--- | :--- | :--- | :--- |
| **Canvas / Background** | `#FBFBFA` / `#FFFFFF` | Obsidian Canvas Default | Main viewport backdrop |
| **Surface (Cards)** | `#FFFFFF` | `var(--background-secondary)` | Bento boxes, tiles, inputs |
| **Dividers & Borders** | `rgba(0, 0, 0, 0.06)` | `var(--background-modifier-border)` | Grid separators, form borders |
| **Pale Red Accent** | `#FDEBEC` (Text: `#9F2F2D`) | `rgba(253, 235, 236, 0.12)` (Text: `#FF8B89`) | High priority badges |
| **Pale Yellow Accent**| `#FBF3DB` (Text: `#956400`) | `rgba(251, 243, 219, 0.12)` (Text: `#FFD36F`) | Medium priority badges |
| **Pale Green Accent** | `#EDF3EC` (Text: `#346538`) | `rgba(237, 243, 236, 0.12)` (Text: `#8EE094`) | Completed status / Low priority |
| **Pale Blue Accent**  | `#E1F3FE` (Text: `#1F6C9F`) | `rgba(225, 243, 254, 0.12)` (Text: `#70C4FF`) | Knowledge areas and tags |

---

## 3. Typographic Architecture

Typography relies on extreme contrast between Editorial Serif headers and structured Monospace metadata:

1. **Editorial Serif (Titles)**
   - **Font Stack**: `'Lyon Text', 'Newsreader', 'Playfair Display', 'Instrument Serif', Georgia, serif`
   - **Usage**: Used for main note headings (H1). Should apply tight tracking (`letter-spacing: -0.03em`) and tight line-height (`1.1`) to emphasize its editorial, printed-work feel.
2. **Geometric Sans-Serif (Body & UI)**
   - **Font Stack**: `'SF Pro Display', 'Geist Sans', 'Helvetica Neue', 'Switzer', system-ui, -apple-system, sans-serif`
   - **Usage**: Body copy, form fields, layout grids, navigation headers. Line height should be a readable `1.6`.
3. **Monospace (Meta & Dates)**
   - **Font Stack**: `'Geist Mono', 'SF Mono', 'JetBrains Mono', monospace`
   - **Usage**: Modification times, deadline indicators, stats counters, status labels.

---

## 4. Grid & Layout Rules

Dashboards must use CSS Grids or Flexboxes configured programmatically to prevent Markdown parsing issues:

- **Bento Grids**: Use asymmetrical CSS Grid structures (`.dashboard-grid` with `grid-template-columns: 3fr 2fr; gap: 24px`).
- **Cards**: Surface elements must use a simple `1px solid` border, crisp border-radius (`8px`), and generous internal padding (`20px`). Avoid drop shadows.
- **Responsive Layout**: Use CSS media queries to stack grid layouts vertically on screens smaller than `900px`.

---

## 5. Visual Constraints (Strict Rules)

1. **No Emojis**: Emojis are strictly banned from markdown content, button text, and heading tags. Replace all metadata icons with crisp, inline SVG primitives (using a consistent `stroke-width="2"`, size of `14px`, and vertically aligned to the text).
2. **No Raw HTML Layout Wrappers**: Avoid nesting markdown code blocks (like ` ```dataviewjs `) inside block-level HTML tags like `<div>`. Instead, instantiate wrappers dynamically using Javascript (`dv.container.createEl()`) to ensure compilation and rendering integrity.
3. **Page hooks via `cssclasses`**: Use the native frontmatter YAML class property (`cssclasses: [dashboard]`) to mount layout classes to the Obsidian wrapper dynamically, maintaining clean file notes.
