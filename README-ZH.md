# Zephyr 第二大腦

> 取名自希臘神話中的西風之神 **Zephyrus**（澤費羅斯）。它象徵著系統如同微風般輕量，在背景無感運行，卻能吹走所有混亂的格式、認知雜訊與冗餘任務。
>
> 📖 閱讀完整的 **[Zephyr 的哲學與定位](file:///c:/Users/sadri/workspace/Zephyr/docs/philosophy-and-positioning-zh.md)** 說明文件，深入瞭解我們的「心流優先」設計與按需調度架構。

Zephyr 是一個以 Obsidian 為基礎建構、專為 **Hermes-agent** 生態系量身打造、極致輕量、無感運行且「心流優先」的個人第二大腦。它的宗旨是最大程度降低人類的認知負載，讓人類專注於靈感與想法的「原始捕獲」（Raw Capture），維持極致的創作心流，而將組織、鏈接、分類和維護等繁瑣任務交給自動化腳本與 AI 智能體。

---

## 🎯 定位與核心哲學

- **輕量與無感運行**：如同西風般在背景默默運作，不強迫人類進行複雜的文件目錄微管理，讓您隨時處於專注的心流狀態。
- **Hermes-Agent 原生設計**：專為 Hermes-agent 打造的終極記憶與知識庫，提供乾淨的元數據、簡單的 API 和統一的索引機制。
- **本地優先與純文本**：完全構建於扁平的本地 Markdown 文件夾和標準雙鏈結構（WikiLinks: `[[筆記名稱]]`）之上，與 Obsidian 等筆記軟體高度相容。
- **先捕獲，後分類**：人類在 `Capture/` 收件箱中輕鬆記錄碎片化的想法；後台守護進程與 AI 智能體會自動對其進行分類、打標籤、格式化，並整理至 `Brain/` 中。
- **雙向主動生長**：透過自動化的夜間「夢境模式」與週度「慢思考審計」，系統會主動修復斷頭鏈接、建議語義關聯，並在筆記聚集時自動起草主題地圖（MOC）。

---

## 📂 知識庫目錄結構

所有筆記必須存放於以下三個目錄之一：

```
Zephyr/
├── Capture/          # 收集/捕獲收件箱
│   ├── YYYY-MM-DD.md # 每日日誌（Daily Logs）、焦點與贏面記錄
│   └── *.md          # 原始想法、網頁剪報、書籍摘錄
├── Brain/            # 常青知識庫
│   ├── Brain.md      # 大腦中央導航看板
│   └── *.md          # 活躍專案（Projects）、常青筆記、知識領域（Areas）與主題地圖（MOCs）
└── System/           # 系統配置與自動化常規
    ├── Archive/      # 已封存或已完成的專案歸檔
    ├── skills/       # AI 智能體常規技能（夢境模式、慢思考模式等）
    ├── templates/    # 筆記、專案、日誌與來源的標準模板
    ├── index.json    # 本地中繼資料索引快取
    └── zephyr-*      # 本地後台守護腳本（Watcher、Worker）
```

---

## ⚙️ 自動化工作流與常規任務

Zephyr 的自動化由本地 Python 守護進程和 AI 智能體的週期性任務共同驅動：

1. **本地監聽與處理器** (`zephyr-watcher.py` & `zephyr-worker.py`)：
   - 在背景常駐運行（透過 `run-watcher.bat` 啟動）。
   - 自動處理 `Capture/` 中的新文件，套用標準中繼資料模板，修復不一致的內部鏈接，編譯 `System/index.json` 並自動執行 Git 提交。
2. **夢境模式 (Dream Mode - 夜間執行)**：
   - 掃描過去 24 小時內修改過的筆記。
   - 在不破壞人類寫作內容的前提下，於筆記底部追加建議的語義鏈接（`## Suggested Connections`）。
   - 當檢測到多個筆記共享同一個新主題時，自動在 `Capture/` 起草 MOC（主題地圖）草稿。
3. **慢思考模式 (Slow Mode - 週度執行)**：
   - 每週一清晨自動執行。
   - 審計知識庫健康度（孤立筆記、斷頭鏈接等）。
   - 梳理所有活躍專案進度、截止日期與過期風險，生成全局週報並發送至配置的 Discord 頻道。

---

## ⚖️ 智能體治理模型

為了在賦予 AI 自動化能力的同時，保障人類對知識產權與內容的絕對控制，Zephyr 嚴格執行三級治理邊界：

- **`AUTO` (自動執行)**：AI 可以自動分類 `Capture/` 中的筆記至 `Brain/`，新增標準標籤，修復損壞鏈接，維護索引中繼資料，並提交至 Git。
- **`PROPOSE` (提案模式)**：對於具有破壞性或修改筆記正文的行為（例如刪除檔案、變更專案狀態/截止日期、直接編輯用戶手寫內容），AI 必須生成帶有 `-- draft.md` 後綴的草稿提案，或向用戶發起詢問。
- **`NEVER` (絕對禁止)**：AI 嚴禁修改 `.obsidian/` 配置文件、洩露 API 密鑰與敏感 secrets，或篡改目前會話分支之前的 Git 歷史提交。

---

## 🚀 安裝與前置準備

1. **Obsidian 整合**：
   - 在 Obsidian 中安裝 **Dataview** 社群外掛，並在設定中開啟 **Enable DataviewJS** 支援。
   - 將 `System/zephyr-dashboard.css` 複製到 Obsidian 的 CSS 片段（CSS Snippets）資料夾，並在設定中啟用它。
2. **後台監聽**：
   - 運行根目錄下的 `run-watcher.bat` 啟動文件監聽器，即時接收並處理放入 `Capture/` 的新靈感。

---

## 📖 系統說明文件

深入閱讀存放於 `docs/` 目錄下的詳細指南：
- 💡 **[Zephyr 的哲學與定位](file:///c:/Users/sadri/workspace/Zephyr/docs/philosophy-and-positioning-zh.md)**：心流優先的設計理念。
- ⚙️ **[技術架構說明書](file:///c:/Users/sadri/workspace/Zephyr/docs/architecture-zh.md)**：底層腳本交互與 `index.json` 機制。
- 🎯 **[專案管理指南](file:///c:/Users/sadri/workspace/Zephyr/docs/project-management-zh.md)**：如何建立並自動化專案的生命週期。
