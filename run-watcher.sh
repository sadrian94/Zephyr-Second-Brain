#!/usr/bin/env bash
# Zephyr Second Brain — File Watcher (macOS / Linux)
# Monitors Zephyr content roots and runs the safe refresh pipeline.

set -euo pipefail
VAULT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$VAULT_DIR"
exec python3 System/zephyr-watcher.py "$@"
