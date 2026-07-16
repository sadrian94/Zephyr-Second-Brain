#!/usr/bin/env bash
# Zephyr Second Brain — File Watcher (macOS / Linux)
# Monitors Capture/ and Brain/ for changes and triggers the worker.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$VAULT_DIR"
exec python3 System/zephyr-watcher.py "$@"
