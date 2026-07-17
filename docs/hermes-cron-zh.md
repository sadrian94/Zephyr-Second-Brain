# Hermes Cron：Zephyr Inbox Triage

在安裝個人 Zephyr vault 後設定此 routine。它使用 Hermes 已設定的 provider 或 OAuth session；**不要**把模型認證放進 `System/config.json`。

## 前置條件

1. 建立 job 的 Hermes profile 已完成登入。
2. 個人 vault 已從此模板更新。
3. 在 vault root 執行 `python3 System/zephyr-worker.py index` 成功。

## Job 設定

在已登入的 profile，使用 Hermes Scheduler UI 或由 agent 執行 `cronjob create` 建立 job。

| 設定 | 值 |
|---|---|
| Name | `zephyr-inbox-triage` |
| Schedule | `every 5m` |
| Workdir | 個人 vault root；通常為 `~/Obsidian/Zephyr` |
| Toolsets | `file`, `terminal` |
| Delivery | `local` |
| Attach to session | `false` |
| Token budget | `700` |
| Turn budget | `6` |
| Time budget | `120` 秒 |
| Agent mode | 啟用（`no_agent: false`） |

不要把 `System/skills/` 的檔案當成 Hermes 全域 skill 掛載。這些是 vault-local routines，不會自動載入；以下 prompt 會要求 job 明確讀取 protocol。

## Prompt

```text
You are the Zephyr inbox triage worker.

Work only inside the current vault workdir. First read AGENTS.md and
System/skills/inbox-triage.md. Follow that protocol exactly.

Process only eligible unclassified Markdown notes in Capture/. Do not use or
request a direct LLM API key. Do not modify existing human-authored body text.
For low confidence, leave the note in Capture/ with
triage_status: needs_review instead of guessing.

After any processing, run:
python3 System/zephyr-worker.py index

If nothing was eligible, output exactly [SILENT]. Otherwise output exactly:
Zephyr inbox: processed=<n>, review=<n>, indexed=true
```

## 模型選擇與 token 控制

第一輪先使用已登入 profile 的 default model。手動執行確認成功後，才在確認該 OAuth 帳號確實可用的前提下，將較低成本的 provider/model ID pin 在 cron job 上。

model override 應屬於 cron job，不屬於 Zephyr 的 config。更重要的是維持 job 範圍狹窄：固定 protocol、只開 `file` 與 `terminal`、token / turn 上限，以及短格式輸出。OAuth 方案仍可能有 model 可用性、使用量與速率限制。

## 驗證

1. 在 `Capture/` 新增一份短小、未分類的 Markdown 筆記。
2. 手動執行新 job 一次。
3. 確認正文未改、frontmatter 符合 `inbox-triage.md`、`System/index.json` 已納入結果。
4. 新增一份模糊筆記，確認它留在 `Capture/` 並標記 `triage_status: needs_review`。
5. 再跑一次，確認 review 筆記會被跳過；無工作時輸出 `[SILENT]`。

當此 cron 是主要 inbox processor 時，不要同時啟用「會呼叫 Hermes」的 watcher。內建 watcher 只負責重建可驗證的 index。
