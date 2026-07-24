# Zephyr 使用指南

Zephyr 的原則很簡單：捕捉要輕，承諾要清。先留下素材；只有在你真正決定時，才把它啟用為專案、升格為知識，或封存。

## 日常流程

1. 把想法、剪藏或日誌放進 `Capture/`。原始 Capture 不需要 YAML。
2. 執行安全更新：

   ```powershell
   python System/zephyr-worker.py refresh
   ```

3. 查看 `System/review-queue.json` 或 Home 儀表板。它會列出原始 Capture、日誌想法、專案期限、暫停工作、驗證與連結問題。
4. 針對選定項目請代理提出提案。提案不是承諾。
5. 你審閱後，才執行相應的生命週期命令。

## 捕捉素材

可在 `Capture/Capture.md` 使用 Quick Capture，直接在 `Capture/` 建立 Markdown，或使用每日記錄。第一筆只需留下足夠讓未來的你辨認的線索，不必當場把帳算完。

可直接對代理這樣說：

```text
整理 Capture/本地模型.md；保留來源，只提出分類提案。
```

```text
蒸餾 Capture/文章剪藏.md；分開來源主張、摘錄、綜合判斷、信心與未解問題。
```

```text
擴展今天日誌的想法；標示假設和可能下一步，但不要替我設定期限或承諾。
```

## Review queue 與草稿自動化

本機 `refresh` 可以放心自動執行：它只會更新 `System/` 下的生成資料，絕不呼叫代理或修改筆記。

代理草稿自動化預設關閉。明確啟用後，外部代理平台最多只能在 `Capture/` 建立一份不撞名的 `-- draft.md` 伴隨草稿；它必須保留來源，不能啟用、升格、封存、刪除或改寫內容。

若要啟用，先複製範例：

```powershell
Copy-Item System/automation.example.json System/automation.json
```

再將 `agent_drafts.enabled` 改為 `true`，並另行設定外部代理排程。Zephyr core 不會自行排程或喚醒代理。詳見 [自動化模型](../System/AUTOMATION.md)。

## 啟用專案

審閱提案後，將 frontmatter 改為完整專案紀錄：

```yaml
---
type: project
status: active
priority: medium
deadline: 2026-08-31
area: "[[Research]]"
tags: [project]
---
```

先預演，再套用：

```powershell
python System/zephyr-worker.py activate "Capture/本地模型研究.md" --approve --dry-run
python System/zephyr-worker.py activate "Capture/本地模型研究.md" --approve
```

檔案會移到 `Active/`。`--dry-run` 不會改變任何檔案，應該是每次移動的第一步。

## 升格蒸餾稿或長期知識

審閱草稿後，將 frontmatter 改為有效筆記：

```yaml
---
type: note
tags: [source, local-ai]
source_note: "[[文章剪藏]]"
---
```

先預演，再移到 `Brain/`：

```powershell
python System/zephyr-worker.py promote "Capture/文章剪藏 -- distilled.md" --approve --dry-run
python System/zephyr-worker.py promote "Capture/文章剪藏 -- distilled.md" --approve
```

## 封存完成或停止的專案

先把專案的 `status` 改成 `completed` 或 `stopped`，再執行：

```powershell
python System/zephyr-worker.py archive "Active/本地模型研究.md" --approve --dry-run
python System/zephyr-worker.py archive "Active/本地模型研究.md" --approve
```

## 維護與排錯

| 需要 | 命令 | 會改筆記嗎？ |
| --- | --- | --- |
| 更新安全生成資料 | `python System/zephyr-worker.py refresh` | 不會 |
| 檢查 YAML 與檔名 | `python System/zephyr-worker.py validate` | 不會 |
| 嚴格健康檢查 | `python System/zephyr-worker.py health` | 不會 |
| 預覽大小寫連結修復 | `python System/zephyr-worker.py fix-links --approve --dry-run` | 不會 |
| 套用已審閱的大小寫連結修復 | `python System/zephyr-worker.py fix-links --approve` | 會 |

可選 watcher 會在 Markdown 變更後執行 `refresh`。Windows 用 `run-watcher.bat`；macOS/Linux 用 `./run-watcher.sh`。它始終只在本機運作。

完整權限規則請見 [System/PROTOCOL.md](../System/PROTOCOL.md)。
