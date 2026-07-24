# Zephyr 第二大腦

Zephyr 是給 Obsidian 使用的本機優先第二大腦。主要介面是你與 AI agent 的對話；CLI 則是處理啟用、升格與封存等重要變更時，可稽核的交易層。

先看 [使用指南](docs/usage-guide-zh.md)。完整規則請見 [System/PROTOCOL.md](System/PROTOCOL.md)、[自動化模型](System/AUTOMATION.md)、[功能狀態表](docs/capabilities.md)、[v0.3.1 版本說明](docs/release-notes-v0.3.1.md) 與 [更新指南](docs/migration-v0.3.md)。

## 核心原則

- 五個根目錄：`Capture/`、`Active/`、`Brain/`、`Archive/`、`System/`。
- 可以直接對代理說「記下這個想法」、「蒸餾這篇文章」、「給我週回顧」或「哪些事需要我決定」。
- 使用標準 YAML frontmatter，並以本機工具驗證與建立索引。
- 自動建立 `System/review-queue.json`，集中 Capture、日誌想法、期限、驗證與連結問題。
- 專案啟用與封存都需要 `--approve`；先用 `--dry-run` 預覽。
- 經批准的蒸餾稿可用 `promote --approve` 從 `Capture/` 升格到 `Brain/`。
- 可選 watcher 執行安全的 `refresh` 流程，不會呼叫代理或網路 API。

Zephyr 核心不會自動啟用、升格或封存內容，不會呼叫 LLM API、保存 API 金鑰、傳送筆記到雲端，或自動改寫人類文字。

Zephyr 對代理中立：一次由一個代理操作；額外代理可選擇擔任有界限、預設唯讀的審閱者或專家。它不設永久階級，也不要求使用多個代理。

## 快速開始

```bash
python3 -m pip install -r requirements.txt
python3 init-zephyr.py
cd ~/Obsidian/Zephyr
python3 System/zephyr-worker.py validate
python3 System/zephyr-worker.py refresh
```

## Agent-first 日常流程

1. 直接告訴代理你要做什麼，例如「記下這個想法」、「蒸餾這篇剪藏」、「給我本週回顧」或「哪些事需要我決定」。
2. 代理可建立你指定的原始 Capture 或獨立草稿，並 refresh review queue；它必須保留來源並標示推測。
3. 你確認提案後，直接說「我批准這個成為專案」或「把這篇升格到 Brain」。代理會替你驗證、預演，再執行對應的確定性命令。

CLI 仍然可自行操作，但它是交易收據，不是日常對話的入口。一次對話只授權你指定的 Capture 或草稿，不代表代理日後可自行啟用、升格、封存、刪除、改寫文字或改專案欄位。
