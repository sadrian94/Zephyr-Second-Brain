# Zephyr 第二大腦

> 取名自希臘西風之神 **Zephyrus**。Zephyr 是為人類 + Hermes-agent 打造的輕量、心流優先 Obsidian 第二大腦。

延伸閱讀：
- [哲學與定位](./docs/philosophy-and-positioning-zh.md)
- [技術架構](./docs/architecture-zh.md)
- [專案管理](./docs/project-management-zh.md)

Zephyr 讓人類只負責原始捕獲；本地 worker 與 AI agent 負責分類、連結、索引與維護。

---

## 前置需求（Obsidian）

### 必要（沒有這些，dashboard 無法運作）

| 元件 | 用途 |
|------|------|
| **[Dataview](https://github.com/blacksmithgu/obsidian-dataview)** 社群外掛 | 驅動 `Home.md` / `Capture.md` / `Brain.md` 的 DataviewJS |
| **開啟 Enable DataviewJS** | dashboard 需要執行 JS 版面 |
| **CSS 片段 `zephyr-dashboard`** | bento dashboard 樣式（`System/zephyr-dashboard.css` → `.obsidian/snippets/`） |

請從 Obsidian → 設定 → 社群外掛安裝 Dataview。此模板**不會**把外掛二進位檔放進 git。

### 可選（個人喜好 — 非必要、不追蹤）

以下適合個人 vault，但**不屬於** Zephyr 模板：

- Templater
- Calendar
- Obsidian Git
- Excalidraw
- QuickAdd
- Icon Folder
- 其他社群外掛

`.obsidian/plugins/**` 已 gitignore，個人外掛偏好不會上 GitHub。

---

## 五分鐘快速開始

**推薦工作流：** 這個 GitHub repo 當**模板**；個人第二大腦安裝到預設路徑 `~/Obsidian/Zephyr`。這樣個人筆記與 secrets 天然不會進 git。

### 方案 A — 預設安裝到 `~/Obsidian/Zephyr`（推薦）

```bash
# 1) 安裝依賴（在此 repo 內）
python3 -m pip install -r requirements.txt

# 2) 初始化個人 vault 到 ~/Obsidian/Zephyr
#    （複製模板/腳本、寫入 System/config.json、啟用 Dataview/CSS 旗標）
python3 init-zephyr.py

# 3) 建立索引（不需要 API key）
python3 ~/Obsidian/Zephyr/System/zephyr-worker.py index

# 4) 在個人 vault 啟動背景 watcher
cd ~/Obsidian/Zephyr
./run-watcher.sh
# Windows: run-watcher.bat
```

用 Obsidian 開啟 `~/Obsidian/Zephyr` 後：
1. 安裝/啟用 **Dataview**，並開啟 **Enable DataviewJS**。
2. 在設定 → 外觀 → CSS 片段啟用 **zephyr-dashboard**。
3. 開啟 `Home.md`。

可選：在 repo 根目錄先準備 gitignored 的 `config_local.json`，再跑 `init-zephyr.py`；內容會寫進個人 vault 的 `System/config.json`。

### 安全更新既有 vault

系統功能先在這個模板 repo 開發，再從 repo 根目錄更新個人 vault：

```bash
python3 init-zephyr.py --update
```

`--update` 只會更新 Zephyr 自己管理的資產：watcher/worker launcher、`System/` 內的腳本、設計/CSS、skills、templates，以及三個 dashboard（`Home.md`、`Capture/Capture.md`、`Brain/Brain.md`）。它會保留 `System/config.json`、`Capture/` 與 `Brain/` 中其餘個人筆記、社群外掛二進位與既有 Obsidian 偏好；最後會重建 `System/index.json`。

### 方案 B — 直接把這個 repo 當 vault（`--here`）

只有在汝刻意要把模板 checkout 本身當 vault 時才用：

```bash
python3 init-zephyr.py --here
python3 System/zephyr-worker.py index
./run-watcher.sh
```

`--here` 只會寫入 gitignored 的 `System/config.json`，**不會**把個人姓名寫進 tracked 的 `AGENTS.md` / `GEMINI.md`。

### 可選：AI 自動分類

在**個人 vault** 編輯 `System/config.json`（init 會產生），填入真實 `ai_api_key`。
或從模板複製：`System/config.example.json` → 個人 vault 的 `System/config.json`。
沒有 key 時，worker 仍會建索引、修復連結，並使用離線啟發式分類。

### 隱私注意（推 GitHub 前必看）

這個 repo 是**模板**，不是個人 vault 備份：
- 個人第二大腦預設在 `~/Obsidian/Zephyr`，應與公開 remote 分離。
- 模板會進 git：dashboard（`Home.md`、`Capture/Capture.md`、`Brain/Brain.md`）、模板、skills、腳本、精簡 `.obsidian` 設定 + `zephyr-dashboard` CSS。
- 被 gitignore：`System/config.json`、`config_local.json`、個人筆記、`System/index.json`、`IDEA.md`，以及**全部** `.obsidian/plugins/**` 二進位。
- `AGENTS.md` / `GEMINI.md` 維持 `{{placeholder}}` 模板，避免個人姓名寫進 git。

---

## 定位

- **輕量無感**：不強迫人類做複雜目錄微管理。
- **Hermes-Agent 原生**：乾淨 frontmatter + `System/index.json` 上下文快取。
- **本地優先純文字**：Markdown + 扁平雙鏈（`[[筆記名稱]]`）。
- **先捕獲、後分類**：人類丟想法；worker/agent 整理。
- **主動生長**：夜間 dream-mode、週度 slow-mode 技能。

---

## 目錄結構

```
Zephyr/
├── Capture/          # 收件箱 + 每日日誌
├── Brain/            # 專案、常青筆記、領域、MOC
└── System/           # 設定、模板、技能、索引、腳本
    ├── DESIGN.md     # 設計系統（dashboard/CSS 必須遵守）
    ├── index.json    # 編譯後的中繼資料快取
    ├── skills/       # Agent 常規
    ├── templates/
    └── zephyr-*.py   # Watcher + Worker
```

---

## 自動化

1. **Watcher / Worker**
   - 監聽 `Capture/` + `Brain/`
   - 分類未標註筆記（LLM 或離線 fallback）
   - 編譯 `System/index.json`
   - 修復大小寫不一致的 wikilink
   - 可選 git auto-commit / pull --rebase / push
2. **Dream Mode（夜間）**：建議連結、起草 MOC。
3. **Slow Mode（週度）**：健康檢查與專案週報。

---

## 治理邊界

- **AUTO**：分類 Capture → Brain、標準標籤、索引、連結修復、git 同步。
- **PROPOSE**：刪除、改寫人類正文、改狀態/截止日期（使用 `-- draft.md`）。
- **NEVER**：洩密、改寫舊 git 歷史、在 init 之外隨意改 `.obsidian/`。

---

## 每日循環

1. 開 `Home.md` 或按 **Today's Log**。
2. 在 `## Capture` 寫 bullet（`- idea: ...`）。
3. 交給 watcher/worker 分類與索引。
4. 用 `System/skills/idea-expansion.md` 把有價值的 idea 擴成專案/筆記。

English README: [README.md](./README.md)
