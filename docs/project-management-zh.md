# Zephyr 專案管理指南 (Project Management Guide)

本文件介紹如何在 Zephyr 系統中進行「心流優先」的個人專案管理。該模式旨在消除傳統專案管理工具（如 Jira, Notion）帶來的維護疲勞與複雜表格干擾，並詳述 **Hermes-agent** 與本地引擎如何在此過程中提供無感支持。

---

## 1. 專案設計核心理念

Zephyr 的專案管理基於以下原則：
* **心流高於流程**：不強迫細粒度的工時追蹤或任務拖拽。專案文件就是一篇標準的 Markdown，任務清單就是 Markdown 的待辦事項 `[ ]`。
* **常青庫無雜訊**：只在 `Brain/` 中呈現當前最重要、最活躍的專案。所有完結或擱置的專案必須自動清理，物理移出工作區。
* **智能代理與預警**：將最枯燥的「立項任務拆解」、「日常進度催促」與「截止日期風險評估」完全委託給 **Hermes-agent** 在後台靜默處理。

---

## 2. 專案元數據規範 (Schema)

每個專案檔案在頭部必須包含以下 YAML 屬性：

```yaml
---
type: project
status: active      # active (進行中) | paused (暫停) | completed (已完成) | archived (已封存)
priority: medium    # high (高) | medium (中) | low (低)
deadline: 2026-08-30 # 格式必須為 YYYY-MM-DD
area: tech-dev      # 對應的知識領域 (如 tech-dev, finance, lifestyle)
---
```

### 專案筆記的標準結構模板 (`System/templates/project.md`)
```markdown
# 專案名稱

> [!NOTE]
> 專案背景與核心目標簡述。

## 🎯 核心里程碑 (Milestones)
- [ ] 里程碑 A
- [ ] 里程碑 B

## 📋 任務清單 (Tasks)
- [ ] 任務 1
- [ ] 任務 2

## 🔗 相關資源 & 常青筆記
- [[相關筆記A]]
- [[相關筆記B]]
```

---

## 3. 專案管理生命週期流程 (Lifecycle Use Case)

在 Zephyr 中，一個專案從靈感到歸檔會流暢地經歷五個階段：

### 3.1 階段一：靈感捕獲 (Capture)
* **人類行為**：你在每日日誌 `Capture/2026-07-15.md` 的 `## 📥 Capture` 部分隨手寫下一行靈感：
  ```markdown
  - 💡 想要寫一個智能電子郵件路由器，自動分流客戶郵件。
  ```
* **系統狀態**：心流未被打斷，你繼續進行其他工作。

### 3.2 階段二：智能提案 (Proposal)
* **系統與 AI 代理行為**：
  1. **本地引擎偵測與標記**：當你保存日誌時，本地 `zephyr-worker.py` 會自動掃描該靈感，發現其尚未包含 WikiLink，隨即在 **`System/index.json` 的 `unprocessed_ideas` 欄位**中登記該靈感的中繼資料（日誌路徑、行號與文本）。
  2. **Hermes-Agent 加載指令並執行**：Hermes-agent 啟動時（定時運行或手動喚醒），讀取 `index.json` 發現未處理靈感，並加載 **`System/skills/idea-expansion.md` 技能指示書**作為執行 SOP。
  3. **起草提案與回鏈**：AI 拆解核心目標與行動任務，在 `Capture/` 生成草稿 `Capture/email-router--draft.md`，並修改你的日誌行以追加連結：`- 💡 想要寫一個智能電子郵件路由器... (Draft: [[email-router--draft]])`。
* **系統狀態**：向使用者發送輕量提醒：「*我已將您關於郵件路由器的想法拆解並生成提案：[[email-router--draft]]*」。當 `index.json` 下次更新時，該靈感會因已具備雙鏈而自動移出未處理列表。

### 3.3 階段三：立項激活 (Activation)
* **人類行為**：
  1. 打開 `[[email-router -- draft]]` 審查 AI 拆解的任務。
  2. 修改或補充任務內容。
  3. **一鍵確認**：將檔名重新命名為 `email-router`（去掉了 `-- draft` 後綴），並將屬性確認為 `status: active`。
* **系統行為 (Local Python Worker)**：
  後台 Worker 檢測到文件名修改且狀態為 active，**自動將其從 `Capture/` 移動到常青大腦庫 `Brain/email-router.md`**。
* **系統狀態**：該項目立即呈現在 `Home.md` 和 `Brain.md` 看板的 **Active Projects** 網格中。

### 3.4 階段四：執行與進度審計 (Execution & Audit)
* **人類行為**：在筆記中將完成的任務勾選為 `[x]`。
* **AI 代理行為 (Slow Mode 週度審計)**：
  每週一清晨，Hermes-agent 讀取大腦索引，進行進度計算：
  * **超期預警**：比對當前日期與專案 `deadline`。若距離截止小於 7 天，在 Discord 週報中標記為 `[🔥 HIGH RISK]`；若已超期，標記為 `[⚠️ OVERDUE]`。
  * **成果彙整**：自動掃描上週 Daily Logs 裡的 `## 🏆 Wins` 部分，提取出與該專案相關的完工記錄。
  * **通報**：將報告推送到你的 Discord 頻道。

### 3.5 階段五：自動化物理歸檔 (Archiving)
* **人類行為**：項目全部完成後，在 Frontmatter 中修改：
  ```yaml
  status: completed
  ```
* **系統行為 (Local Python Worker)**：
  Worker 秒級響應檢測，自動將 `Brain/email-router.md` **物理移動到 `System/Archive/email-router.md`**。
* **系統狀態**：該項目從主頁和常青庫看板中消失，避免產生視覺雜訊，但隨時可以在 `System/Archive/` 中調閱。

---

## 4. 為什麼這套系統適合你？

| 特性 | 傳統工具 (Jira, Notion) | Zephyr 專案管理 |
| :--- | :--- | :--- |
| **立項門檻** | 很高（需建檔、選模板、手動關聯目錄與屬性） | 極低（隨手寫下一行靈感，AI 自動在後台起草提案） |
| **維護成本** | 很高（需要手動拖拽卡片、手動移動完工檔案） | 零（透過 `status` 屬性，背景腳本執行物理級歸檔） |
| **視覺雜訊** | 很高（充滿卡片邊框、裝飾性表情、大陰影） | 極低（Warm Monochrome 紙張質感便當格，僅顯示核心元數據） |
| **進度追蹤** | 被動（需要你主動打開看板點擊查看） | 主動（AI 每週一將健康度報告與逾期預警推送到你的手機 Discord） |
