# Zephyr v0.2 架構

Zephyr 的真實資料來源是本機的平面 Markdown 檔案。Python worker 只執行可重現的工作：解析 YAML、驗證 schema、建立索引、回報連結問題，以及執行經批准的移動。

可選 watcher 在本機 Markdown 變更後等待短暫 debounce，再執行 `index`。它不能呼叫代理 CLI、LLM API，也不會修改筆記。`System/index.json` 與 `System/status.json` 是快取/狀態資料，不是真實來源。

代理 CLI 是可選 adapter，可以讀取協定並提出建議；核心不需要供應商、雲端服務、API 金鑰、資料庫伺服器或網路。詳見 [協定](../System/PROTOCOL.md)。
