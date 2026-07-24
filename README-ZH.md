# Zephyr 第二大腦

Zephyr 是給 Obsidian 使用的本機優先 Markdown 第二大腦協定。v0.3.0 將安全的本機自動化與人工決策權結合：機械整理可以自動跑，承諾與文字仍由人批准。

先看 [使用指南](docs/usage-guide-zh.md)。完整規則請見 [System/PROTOCOL.md](System/PROTOCOL.md)、[自動化模型](System/AUTOMATION.md)、[功能狀態表](docs/capabilities.md)、[v0.3.0 版本說明](docs/release-notes-v0.3.0.md) 與 [更新指南](docs/migration-v0.3.md)。

## 核心原則

- 五個根目錄：`Capture/`、`Active/`、`Brain/`、`Archive/`、`System/`。
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

日常流程是：先寫入 `Capture/`，由 `refresh` 建立 review queue；需要時請代理起草分類、擴展或蒸餾提案。人工審閱後，專案用 `activate --approve`，長期知識用 `promote --approve`，完成或停止的專案用 `archive --approve`。
