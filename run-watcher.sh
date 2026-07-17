#!/usr/bin/env bash
# Zephyr Second Brain — File Watcher (macOS / Linux)
# Monitors Capture/ and Brain/ for changes and triggers the worker.

set -euo pipefail
VAULT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$VAULT_DIR"
exec python3 System/zephyr-watcher.py "$@"
