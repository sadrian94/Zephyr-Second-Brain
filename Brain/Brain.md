---
type: note
tags: [dashboard]
cssclasses: [dashboard]
---
```dataviewjs
const currentFile = dv.current().file.name;
const headerContainer = dv.container.createEl("div", { cls: "nav-header-container" });

const navContainer = headerContainer.createEl("div", { cls: "nav-header" });
const links = [
    { name: "Home", target: "Home" },
    { name: "Capture Inbox", target: "Capture" },
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

# Evergreen Brain

```dataviewjs
const svgIcons = {
    calendar: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`,
    brain: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>`,
    file: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`
};

// Create Dashboard Grid Container
const gridContainer = dv.container.createEl("div", { cls: "dashboard-grid" });
const leftColumn = gridContainer.createEl("div");
const rightColumn = gridContainer.createEl("div");

// --- Left Column: Active Projects ---
const projects = dv.pages('"Brain"')
    .filter(p => p.type === 'project' && p.status === 'active')
    .sort(p => p.deadline || '9999-12-31', 'asc');

const leftHeader = leftColumn.createEl("h2");
leftHeader.innerHTML = `${svgIcons.calendar} Active Projects`;

if (projects.length > 0) {
    let projectGridHtml = `<div class="project-grid">`;
    for (let p of projects) {
        const priorityClass = `priority-${p.priority || 'medium'}`;
        projectGridHtml += `
        <div class="project-card">
            <div class="project-title"><a href="${p.file.path}">${p.file.name}</a></div>
            <div class="project-meta">
                <span class="badge ${priorityClass}">${p.priority || 'medium'}</span>
                <span class="deadline">${svgIcons.calendar} ${p.deadline || 'No deadline'}</span>
            </div>
        </div>`;
    }
    projectGridHtml += `</div>`;
    leftColumn.createEl("div").innerHTML = projectGridHtml;
} else {
    leftColumn.createEl("p").innerHTML = "*No active projects found.*";
}

// --- Left Column: Recent Notes ---
const recentNotes = dv.pages('"Brain"')
    .filter(p => p.type === 'note' && p.file.name !== 'Brain' && (!p.tags || !p.tags.includes('dashboard')) && (!p.tags || !p.tags.some(t => t.startsWith('area/'))))
    .sort(p => p.file.mtime, 'desc')
    .limit(8);

const leftRecentNotesHeader = leftColumn.createEl("h2");
leftRecentNotesHeader.innerHTML = `${svgIcons.file} Recent Notes`;

if (recentNotes.length > 0) {
    let recentNotesHtml = `<ul class="capture-list">`;
    for (let rn of recentNotes) {
        recentNotesHtml += `<li><a href="${rn.file.path}">${rn.file.name}</a> <span class="time-meta">${rn.file.mtime.toFormat("yyyy-MM-dd")}</span></li>`;
    }
    recentNotesHtml += `</ul>`;
    leftColumn.createEl("div").innerHTML = recentNotesHtml;
} else {
    leftColumn.createEl("p").innerHTML = "*No notes found.*";
}

// --- Right Column: Map of Contents (MOCs) ---
const mocs = dv.pages('"Brain"')
    .filter(p => p.tags && p.tags.includes('moc') && p.file.name !== 'Brain')
    .sort(p => p.file.name, 'asc');

const rightMocsHeader = rightColumn.createEl("h2");
rightMocsHeader.innerHTML = `${svgIcons.brain} Map of Contents (MOCs)`;

if (mocs.length > 0) {
    let mocsHtml = `<ul class="capture-list">`;
    for (let m of mocs) {
        mocsHtml += `<li><a href="${m.file.path}">${m.file.name}</a></li>`;
    }
    mocsHtml += `</ul>`;
    rightColumn.createEl("div").innerHTML = mocsHtml;
} else {
    rightColumn.createEl("p").innerHTML = "*No MOCs found.*";
}

// --- Right Column: Knowledge Areas ---
const areas = dv.pages('"Brain"')
    .filter(p => p.tags && p.tags.some(t => t.startsWith('area/')) && p.file.name !== 'Brain')
    .sort(p => p.file.name, 'asc');

const rightAreasHeader = rightColumn.createEl("h2");
rightAreasHeader.innerHTML = `${svgIcons.brain} Knowledge Areas`;

if (areas.length > 0) {
    let areasHtml = `<ul class="capture-list">`;
    for (let a of areas) {
        const areaTag = a.tags.find(t => t.startsWith('area/'));
        const cleanArea = areaTag ? areaTag.replace('area/', '') : '';
        areasHtml += `<li><a href="${a.file.path}">${a.file.name}</a> <span class="badge" style="background: var(--zephyr-bg-pale-blue); color: var(--zephyr-text-pale-blue); font-size: 0.7em;">${cleanArea}</span></li>`;
    }
    areasHtml += `</ul>`;
    rightColumn.createEl("div").innerHTML = areasHtml;
} else {
    rightColumn.createEl("p").innerHTML = "*No knowledge areas found.*";
}

// --- Right Column: Other Projects ---
const otherProjects = dv.pages('"Brain"')
    .filter(p => p.type === 'project' && p.status !== 'active')
    .sort(p => p.file.name, 'asc');

const rightOtherProjectsHeader = rightColumn.createEl("h2");
rightOtherProjectsHeader.innerHTML = `${svgIcons.file} Other Projects`;

if (otherProjects.length > 0) {
    let otherProjectsHtml = `<ul class="capture-list">`;
    for (let op of otherProjects) {
        const statusStyle = op.status === 'completed' ? 'var(--zephyr-text-pale-green)' : 'var(--text-muted)';
        otherProjectsHtml += `<li><a href="${op.file.path}">${op.file.name}</a> <span class="badge" style="background: var(--background-primary); color: ${statusStyle}; border: 1px solid var(--background-modifier-border); font-size: 0.7em;">${op.status}</span></li>`;
    }
    otherProjectsHtml += `</ul>`;
    rightColumn.createEl("div").innerHTML = otherProjectsHtml;
} else {
    rightColumn.createEl("p").innerHTML = "*No completed or paused projects.*";
}
```

<div class="system-status-bar">
    <span>Zephyr Second Brain V0.1.0</span> | <span>Background Worker Status: Active</span>
</div>
