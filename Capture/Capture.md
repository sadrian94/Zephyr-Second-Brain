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

# Capture Inbox

```dataviewjs
const svgIcons = {
    calendar: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,
    inbox: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>`
};

// 1. Grid structure
const gridContainer = dv.container.createEl("div", { cls: "dashboard-grid" });
const leftColumn = gridContainer.createEl("div");
const rightColumn = gridContainer.createEl("div");

// 2. Render Ingestion Form in Left Column
const formContainer = leftColumn.createEl("div", { cls: "ingest-form" });
formContainer.innerHTML = `
    <h3>${svgIcons.inbox} Quick Capture</h3>
    <input type="text" id="ingest-title" placeholder="Note Title (NTFS-safe)" />
    <textarea id="ingest-content" placeholder="Write raw ideas, clippings, or logs here..."></textarea>
    <button class="ingest-btn" id="ingest-submit">Capture Idea</button>
`;

formContainer.querySelector("#ingest-submit").addEventListener("click", async () => {
    const titleInput = formContainer.querySelector("#ingest-title");
    const contentInput = formContainer.querySelector("#ingest-content");
    const titleVal = titleInput.value.trim();
    const contentVal = contentInput.value;
    
    if (!titleVal) {
        new Notice("Title cannot be empty!");
        return;
    }
    
    const cleanTitle = titleVal.replace(/[\\/:*?"<>|]/g, "").trim();
    if (!cleanTitle) {
        new Notice("Invalid file name!");
        return;
    }
    
    const filePath = `Capture/${cleanTitle}.md`;
    
    if (app.vault.getAbstractFileByPath(filePath)) {
        new Notice("A note with this name already exists in Capture!");
        return;
    }
    
    const fileContent = contentVal;
    
    try {
        await app.vault.create(filePath, fileContent);
        new Notice(`Note "${cleanTitle}" captured!`);
        titleInput.value = "";
        contentInput.value = "";
    } catch (e) {
        new Notice("Failed to create note: " + e.message);
    }
});

// 3. Render Unprocessed Inbox Feed in Right Column
const capture = dv.pages('"Capture"')
    .filter(p => p.file.name !== 'Capture' && p.type !== 'log' && (!p.tags || !p.tags.includes('dashboard')))
    .sort(p => p.file.mtime, 'desc');

const rightHeader = rightColumn.createEl("h2");
rightHeader.innerHTML = `${svgIcons.inbox} Unprocessed Inbox`;

if (capture.length > 0) {
    let captureListHtml = `<ul class="capture-list">`;
    for (let c of capture) {
        captureListHtml += `<li><a href="${c.file.path}">${c.file.name}</a> <span class="time-meta">${c.file.mtime.toFormat("yyyy-MM-dd HH:mm")}</span></li>`;
    }
    captureListHtml += `</ul>`;
    rightColumn.createEl("div").innerHTML = captureListHtml;
} else {
    rightColumn.createEl("p").innerHTML = "*No unprocessed items in Capture.*";
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

---

```dataviewjs
const svgIcons = {
    calendar: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`
};

const logs = dv.pages('"Capture"')
    .filter(p => p.type === 'log')
    .sort(p => p.date || p.file.name, 'desc');

const logsHeader = dv.container.createEl("h2");
logsHeader.innerHTML = `${svgIcons.calendar} Daily Logs Archive`;

if (logs.length > 0) {
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
    const logsContainer = dv.container.createEl("div", { cls: "logs-container" });
    
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
    dv.paragraph("*No logs found.*");
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
    <span>Zephyr Second Brain v0.2</span> | <span>Raw capture; review before commitment</span>
</div>
