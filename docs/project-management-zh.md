# v0.3.1 專案管理

`Active/` 只放使用者明確決定推進的專案。先在 `Capture/` 建立或提出建議；建議不等於已啟用的專案。

啟用前，專案必須有完整且有效的 YAML：`type: project`、允許的狀態與優先級、ISO 格式截止日、以及 area。先用 `activate --approve --dry-run` 預覽，再正式套用。完成或停止後，更新狀態，再用 `archive --approve` 封存。watcher、代理程序與單純的狀態編輯都不會自動封存。

完整命令與批准界線請見 [協定](../System/PROTOCOL.md)。
