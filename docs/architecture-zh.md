# Zephyr v0.3.1 架構

Zephyr 的真實資料來源是本機的平面 Markdown 檔案。Python worker 只執行可重現的工作：解析 YAML、驗證 schema、建立索引、回報連結問題，以及執行經批准的移動。

可選 watcher 在本機 Markdown 變更後等待短暫 debounce，再執行 `refresh`。worker 會驗證、建立索引、回報連結，並寫入 `System/review-queue.json`；這些都是生成資料，不是真實來源。watcher 不能呼叫代理 CLI、LLM API，也不會修改筆記。

語意自動化屬於另一個明確啟用的層級。外部代理只能在 `Capture/` 建立不覆蓋來源的 companion draft，不能執行生命週期移動。批准後的專案使用 `activate`，長期知識使用 `promote`，完成或停止的專案使用 `archive`。

代理 CLI 是可選 adapter。Zephyr 不設永久的主要或次要代理：每個任務或工作階段只允許一個主動操作代理寫入，選用的審閱者與專家預設唯讀。它們可以讀取協定並提出建議；核心不需要供應商、雲端服務、API 金鑰、資料庫伺服器或網路。詳見 [協定](../System/PROTOCOL.md)。
