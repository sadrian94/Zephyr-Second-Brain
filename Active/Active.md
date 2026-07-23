---
type: note
tags: [dashboard]
cssclasses: [dashboard]
---

```dataviewjs
const currentFile = dv.current()?.file?.name || "";
const headerContainer = dv.container.createEl("div", { cls: "nav-header-container" });
const navContainer = headerContainer.createEl("div", { cls: "nav-header" });
const links = [
    { name: "Home", target: "Home" },
    { name: "Capture Inbox", target: "Capture" },
    { name: "Active Projects", target: "Active" },
    { name: "Brain", target: "Brain" }
];

for (const link of links) {
    navContainer.createEl("a", {
        text: link.name,
        href: link.target,
        cls: `internal-link${currentFile === link.target ? " active" : ""}`
    });
}
```

# Active Projects

Only projects explicitly approved through `activate --approve` belong here. This view makes the current commitments visible; it does not change their status or priority.

```dataviewjs
const icons = {
    calendar: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,
    flag: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><path d="M4 22V4"></path><path d="M4 4h13l-1 5 1 5H4"></path></svg>`,
    folder: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`
};

const projects = dv.pages('"Active"')
    .filter(p => p.type === "project")
    .sort(p => p.deadline || "9999-12-31", "asc");
const active = projects.filter(p => p.status === "active");
const paused = projects.filter(p => p.status === "paused");
const withoutDeadline = active.filter(p => !p.deadline);
const today = dv.date("today").startOf("day");
const horizon = today.plus({ days: 7 });
const dueSoon = active.filter(p => p.deadline && p.deadline >= today && p.deadline <= horizon);

const stats = dv.container.createEl("div", { cls: "stats-row" });
for (const [value, label] of [
    [active.length, "Active"],
    [dueSoon.length, "Due in 7 days"],
    [withoutDeadline.length, "No deadline"],
    [paused.length, "Paused"]
]) {
    const card = stats.createEl("div", { cls: "stats-card" });
    card.createEl("div", { text: String(value), cls: "stats-value" });
    card.createEl("div", { text: label, cls: "stats-label" });
}

function formatDeadline(deadline) {
    if (!deadline) return "No deadline";
    if (typeof deadline.toFormat === "function") return deadline.toFormat("yyyy-MM-dd");
    const match = String(deadline).match(/^(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : String(deadline);
}

function renderProjectCard(project) {
    const priority = project.priority || "medium";
    const status = project.status || "active";
    const area = project.area ? String(project.area).replace(/^\[\[|\]\]$/g, "") : "No area";
    return `
        <div class="project-card">
            <div>
                <div class="project-title"><a href="${project.file.path}">${project.file.name}</a></div>
                <div class="time-meta" style="margin-top: 8px;">${icons.folder} ${area}</div>
            </div>
            <div class="project-meta">
                <span class="badge priority-${priority}">${priority}</span>
                <span class="deadline">${icons.calendar} ${formatDeadline(project.deadline)}</span>
            </div>
            <div class="time-meta" style="margin-top: 12px;">${icons.flag} ${status}</div>
        </div>`;
}

const grid = dv.container.createEl("div", { cls: "dashboard-grid" });
const mainColumn = grid.createEl("div");
const sideColumn = grid.createEl("div");

const activeHeader = mainColumn.createEl("h2");
activeHeader.innerHTML = `${icons.flag} Current commitments`;
if (active.length) {
    const activeGrid = mainColumn.createEl("div", { cls: "project-grid" });
    activeGrid.innerHTML = active.map(renderProjectCard).join("");
} else {
    mainColumn.createEl("p", { text: "No active projects. Review a proposal in Capture before committing work here." });
}

const dueHeader = sideColumn.createEl("h2");
dueHeader.innerHTML = `${icons.calendar} Near-term deadlines`;
if (dueSoon.length) {
    const list = sideColumn.createEl("ul", { cls: "capture-list" });
    for (const project of dueSoon) {
        list.createEl("li").innerHTML = `<a href="${project.file.path}">${project.file.name}</a><span class="time-meta">${formatDeadline(project.deadline)}</span>`;
    }
} else {
    sideColumn.createEl("p", { text: "No active deadlines in the next seven days." });
}

const pausedHeader = sideColumn.createEl("h2");
pausedHeader.innerHTML = `${icons.folder} Paused projects`;
if (paused.length) {
    const list = sideColumn.createEl("ul", { cls: "capture-list" });
    for (const project of paused) {
        list.createEl("li").innerHTML = `<a href="${project.file.path}">${project.file.name}</a><span class="time-meta">${formatDeadline(project.deadline)}</span>`;
    }
} else {
    sideColumn.createEl("p", { text: "No paused projects." });
}

dv.container.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;
    const href = link.getAttribute("data-href") || link.getAttribute("href");
    if (!href || href.startsWith("http://") || href.startsWith("https://") || href.startsWith("app://") || href.startsWith("#")) return;
    event.preventDefault();
    app.workspace.openLinkText(href, dv.current()?.file?.path || "", false);
});
```

<div class="system-status-bar">
    <span>Zephyr Second Brain v0.2.2</span> | <span>Deliberate work, visible commitments</span>
</div>
