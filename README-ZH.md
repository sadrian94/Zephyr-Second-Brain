# Zephyr 第二大腦

Zephyr 是給 Obsidian 使用的本機優先 Markdown 第二大腦協定。v0.2.1 採取「人工優先」：代理可以提出建議，但只有使用者明確批准後，本機且可稽核的工具才會套用變更。

完整規則請見 [System/PROTOCOL.md](System/PROTOCOL.md)、[功能狀態表](docs/capabilities.md)、[v0.2.1 版本說明](docs/release-notes-v0.2.1.md) 與 [v0.2.1 更新指南](docs/migration-v0.2.1.md)。

## 核心原則

- 五個根目錄：`Capture/`、`Active/`、`Brain/`、`Archive/`、`System/`。
- 使用標準 YAML frontmatter，並以本機工具驗證與建立索引。
- 專案啟用與封存都需要 `--approve`；先用 `--dry-run` 預覽。
- 可選 watcher 只會重新建立索引與回報問題，不會呼叫代理或網路 API。

Zephyr 核心不會自動啟用或封存專案、呼叫 LLM API、保存 API 金鑰、將檔案內容傳送到雲端，或自動改寫人類文字。

Zephyr 對代理中立：一次由一個代理操作；額外代理可選擇擔任有界限、預設唯讀的審閱者或專家。它不設永久階級，也不要求使用多個代理。

## 快速開始

```bash
python3 -m pip install -r requirements.txt
python3 init-zephyr.py
cd ~/Obsidian/Zephyr
python3 System/zephyr-worker.py validate
python3 System/zephyr-worker.py index
```

日常流程是：先寫入 `Capture/`，需要時請代理提出建議；人工審閱後，以 `activate --approve` 放入 `Active/`；完成或停止時更新狀態，再以 `archive --approve` 移到 `Archive/`。
