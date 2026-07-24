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
for (let link of links) {
    const isCurrent = currentFile === link.target;
    navContainer.createEl("a", {
        text: link.name,
        href: link.target,
        cls: `internal-link${isCurrent ? " active" : ""}`
    });
}

// Intercept all internal link clicks to ensure they open correctly in Obsidian
dv.container.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (!link) return;
    const href = link.getAttribute("data-href") || link.getAttribute("href");
    if (!href) return;
    if (href.startsWith("http://") || href.startsWith("https://") || href.startsWith("app://") || href.startsWith("#")) {
        return;
    }
    e.preventDefault();
    const currentPath = dv.current()?.file?.path || "";
    app.workspace.openLinkText(href, currentPath, false);
});

const todayBtn = headerContainer.createEl("button", {
    text: "Today's Log",
    cls: "ingest-btn",
    attr: { style: "margin: 0; font-size: 0.8em; padding: 6px 12px;" }
});

todayBtn.addEventListener("click", async () => {
    const todayStr = window.moment().format("YYYY-MM-DD");
    const filePath = `Capture/${todayStr}.md`;
    const file = app.vault.getAbstractFileByPath(filePath);
    if (file) {
        app.workspace.openLinkText(filePath, "", false);
    } else {
        const templatePath = "System/templates/daily-log.md";
        const templateFile = app.vault.getAbstractFileByPath(templatePath);
        let content = "";
        if (templateFile) {
            content = await app.vault.read(templateFile);
            content = content.replace(/YYYY-MM-DD/g, todayStr);
        } else {
            content = `---\ntype: log\ndate: ${todayStr}\ntags: [daily]\n---\n# Daily Log — ${todayStr}\n\n## Focus\n- \n\n## Wins\n- \n\n## Capture\n\n\n## Log\n- \n`;
        }
        try {
            await app.vault.create(filePath, content);
            new Notice(`Created Daily Log for ${todayStr}`);
            app.workspace.openLinkText(filePath, "", false);
        } catch (err) {
            new Notice("Failed to create Daily Log: " + err.message);
        }
    }
});
```

# Zephyr Second Brain

> [!IMPORTANT]
> **Obsidian Prerequisites**
> 1. Install the **Dataview** community plugin in Obsidian and enable **Enable DataviewJS** in its settings.
> 2. Enable the **zephyr-dashboard** CSS snippet in Obsidian `Settings -> Appearance -> CSS Snippets`.

```dataviewjs
const svgIcons = {
    calendar: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,
    inbox: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>`
};

// 1. Stats calculation & rendering
const totalInbox = dv.pages('"Capture"').filter(p => p.file.name !== 'Capture' && p.type !== 'log' && (!p.tags || !p.tags.includes('dashboard'))).length;
const totalProjects = dv.pages('"Active"').filter(p => p.type === 'project').length;
const totalNotes = dv.pages('"Brain"').filter(p => p.type === 'note' && p.file.name !== 'Brain' && (!p.tags || !p.tags.includes('dashboard'))).length;
const totalLogs = dv.pages('"Capture"').filter(p => p.type === 'log').length;
let totalReview = 0;
let highReview = 0;
try {
    const queueText = await dv.io.load("System/review-queue.json");
    const queue = JSON.parse(queueText || "{}");
    totalReview = Number(queue?.counts?.total || 0);
    highReview = Number(queue?.counts?.high || 0);
} catch (_) {
    // The queue appears after the first refresh; an absent queue means no displayed signal yet.
}

const statsContainer = dv.container.createEl("div", { cls: "stats-row" });
statsContainer.innerHTML = `
    <div class="stats-card">
        <div class="stats-value">${totalInbox}</div>
        <div class="stats-label">Inbox</div>
    </div>
    <div class="stats-card">
        <div class="stats-value">${totalProjects}</div>
        <div class="stats-label">Projects</div>
    </div>
    <div class="stats-card">
        <div class="stats-value">${totalNotes}</div>
        <div class="stats-label">Evergreen</div>
    </div>
    <div class="stats-card">
        <div class="stats-value">${totalLogs}</div>
        <div class="stats-label">Daily Logs</div>
    </div>
    <div class="stats-card">
        <div class="stats-value">${totalReview}</div>
        <div class="stats-label">Review Queue${highReview ? ` / ${highReview} high` : ""}</div>
    </div>
`;

// 2. Dashboard Grid layout container
const gridContainer = dv.container.createEl("div", { cls: "dashboard-grid" });
const leftColumn = gridContainer.createEl("div");
const rightColumn = gridContainer.createEl("div");

// 3. Render Left Column: Active Projects
const projects = dv.pages('"Active"')
    .filter(p => p.type === 'project' && p.status === 'active')
    .sort(p => p.deadline || '9999-12-31', 'asc');

const leftHeader = leftColumn.createEl("h2");
leftHeader.innerHTML = `${svgIcons.calendar} Active Projects`;

if (projects.length > 0) {
    let projectGridHtml = `<div class="project-grid">`;
    for (let p of projects) {
        const priorityClass = `priority-${p.priority || 'medium'}`;
        let deadlineStr = 'No deadline';
        if (p.deadline) {
            if (typeof p.deadline.toFormat === 'function') {
                deadlineStr = p.deadline.toFormat('yyyy-MM-dd');
            } else {
                const match = String(p.deadline).match(/^(\d{4}-\d{2}-\d{2})/);
                deadlineStr = match ? match[1] : String(p.deadline);
            }
        }
        projectGridHtml += `
        <div class="project-card">
            <div class="project-title"><a href="${p.file.path}">${p.file.name}</a></div>
            <div class="project-meta">
                <span class="badge ${priorityClass}">${p.priority || 'medium'}</span>
                <span class="deadline">${svgIcons.calendar} ${deadlineStr}</span>
            </div>
        </div>`;
    }
    projectGridHtml += `</div>`;
    leftColumn.createEl("div").innerHTML = projectGridHtml;
} else {
    leftColumn.createEl("p").innerHTML = "*No active projects found.*";
}

// 4. Render Right Column: Recent Captures
const capture = dv.pages('"Capture"')
    .filter(p => p.file.name !== 'Capture' && p.type !== 'log' && (!p.tags || !p.tags.includes('dashboard')))
    .sort(p => p.file.mtime, 'desc')
    .limit(5);

const rightCaptureHeader = rightColumn.createEl("h2");
rightCaptureHeader.innerHTML = `${svgIcons.inbox} Recent Captures`;

if (capture.length > 0) {
    let captureListHtml = `<ul class="capture-list">`;
    for (let c of capture) {
        captureListHtml += `<li><a href="${c.file.path}">${c.file.name}</a> <span class="time-meta">${c.file.mtime.toFormat("yyyy-MM-dd HH:mm")}</span></li>`;
    }
    captureListHtml += `</ul>`;
    rightColumn.createEl("div").innerHTML = captureListHtml;
} else {
    rightColumn.createEl("p").innerHTML = "*Inbox is empty.*";
}

// 5. Render Right Column: Recent Logs
const logs = dv.pages('"Capture"')
    .filter(p => p.type === 'log')
    .sort(p => p.date || p.file.name, 'desc')
    .limit(5);

const rightLogsHeader = rightColumn.createEl("h2");
rightLogsHeader.innerHTML = `${svgIcons.calendar} Recent Logs`;

if (logs.length > 0) {
    // Group logs by YYYY-MM
    const groups = {};
    for (let l of logs) {
        let monthKey = "Other";
        if (l.date && typeof l.date.toFormat === "function") {
            monthKey = l.date.toFormat("yyyy-MM");
        } else {
            const nameStr = String(l.file.name);
            const match = nameStr.match(/^(\d{4}-\d{2})/);
            monthKey = match ? match[1] : "Other";
        }
        if (!groups[monthKey]) groups[monthKey] = [];
        groups[monthKey].push(l);
    }
    
    const sortedMonths = Object.keys(groups).sort().reverse();
    const logsContainer = rightColumn.createEl("div", { cls: "logs-container" });
    
    for (let i = 0; i < sortedMonths.length; i++) {
        const month = sortedMonths[i];
        const monthLogs = groups[month];
        
        const details = logsContainer.createEl("details", { 
            cls: "log-month-details",
            attr: i === 0 ? { open: "true" } : {} 
        });
        
        const summary = details.createEl("summary", { cls: "log-month-summary" });
        summary.innerHTML = `<span class="month-title">${month}</span> <span class="month-count">(${monthLogs.length})</span>`;
        
        const grid = details.createEl("div", { cls: "log-row", attr: { style: "margin-top: 10px;" } });
        for (let l of monthLogs) {
            const tile = grid.createEl("div", { cls: "log-tile" });
            tile.innerHTML = `<a href="${l.file.path}">${l.file.name}</a>`;
        }
    }
} else {
    rightColumn.createEl("p").innerHTML = "*No logs found.*";
}

// Intercept all internal link clicks to ensure they open correctly in Obsidian
dv.container.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (!link) return;
    const href = link.getAttribute("data-href") || link.getAttribute("href");
    if (!href) return;
    if (href.startsWith("http://") || href.startsWith("https://") || href.startsWith("app://") || href.startsWith("#")) {
        return;
    }
    e.preventDefault();
    const currentPath = dv.current()?.file?.path || "";
    app.workspace.openLinkText(href, currentPath, false);
});
```

<div class="system-status-bar">
    <span>Zephyr Second Brain v0.3.0</span> | <span>Safe automation, visible decisions</span>
</div>
