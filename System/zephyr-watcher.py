#!/usr/bin/env python3
"""Optional local watcher for deterministic Zephyr refresh automation only."""

from __future__ import annotations

import os
import json
import subprocess
import sys
import time
from datetime import datetime

SYSTEM_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DIR = os.path.dirname(SYSTEM_DIR)
WATCH_DIRS = [os.path.join(VAULT_DIR, name) for name in ("Capture", "Active", "Brain", "Archive")]
WORKER_PATH = os.path.join(SYSTEM_DIR, "zephyr-worker.py")
DEBOUNCE_INTERVAL = 2.0
POLL_INTERVAL = 2.0
AUTOMATION_PATH = os.path.join(SYSTEM_DIR, "automation.json")


def load_automation_config() -> dict[str, object]:
    defaults: dict[str, object] = {
        "on_change": "refresh",
        "debounce_seconds": 3.0,
        "poll_seconds": 5.0,
    }
    try:
        with open(AUTOMATION_PATH, "r", encoding="utf-8") as handle:
            configured = json.load(handle)
        if isinstance(configured, dict):
            defaults.update(configured)
    except (OSError, json.JSONDecodeError):
        pass
    if defaults.get("on_change") not in {"refresh", "index"}:
        defaults["on_change"] = "refresh"
    return defaults


AUTOMATION = load_automation_config()
DEBOUNCE_INTERVAL = max(1.0, float(AUTOMATION["debounce_seconds"]))
POLL_INTERVAL = max(2.0, float(AUTOMATION["poll_seconds"]))
ON_CHANGE_COMMAND = str(AUTOMATION["on_change"])


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Watcher] {message}")


def run_worker(mode: str = "refresh") -> bool:
    """Run a safe local refresh/index command and return its actual outcome."""
    if mode not in {"refresh", "index"}:
        log(f"Ignoring unsupported watcher mode {mode!r}; using refresh.")
        mode = "refresh"
    log(f"Triggering deterministic {mode}...")
    try:
        result = subprocess.run(
            [sys.executable, WORKER_PATH, mode],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        log(f"Worker could not start: {exc}")
        return False
    for stream, label in ((result.stdout, "Worker"), (result.stderr, "Worker-Error")):
        for line in stream.splitlines():
            if line.strip():
                print(f"  [{label}] {line}")
    if result.returncode == 0:
        log("Worker finished successfully.")
        return True
    log(f"Worker failed with exit code {result.returncode}.")
    return False


def get_md_files_state() -> dict[str, float]:
    state: dict[str, float] = {}
    for directory in WATCH_DIRS:
        if not os.path.isdir(directory):
            continue
        for entry in os.scandir(directory):
            if entry.is_file() and entry.name.endswith(".md") and entry.name != "Home.md":
                try:
                    state[entry.path] = entry.stat().st_mtime
                except OSError:
                    pass
    return state


try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class ZephyrHandler(FileSystemEventHandler):
        def __init__(self) -> None:
            super().__init__()
            self.last_change_time = 0.0
            self.pending_change = False

        def on_any_event(self, event) -> None:  # type: ignore[no-untyped-def]
            if event.is_directory or not event.src_path.endswith(".md") or os.path.basename(event.src_path) == "Home.md":
                return
            self.last_change_time = time.time()
            self.pending_change = True
            log(f"Detected local Markdown change: {os.path.basename(event.src_path)} ({event.event_type})")

    def run_watchdog() -> None:
        log("Watchdog detected; monitoring content roots for local index updates.")
        handler = ZephyrHandler()
        observer = Observer()
        for directory in WATCH_DIRS:
            if os.path.isdir(directory):
                observer.schedule(handler, path=directory, recursive=False)
                log(f"Monitoring {directory}")
        observer.start()
        try:
            while True:
                time.sleep(0.5)
                if handler.pending_change and time.time() - handler.last_change_time >= DEBOUNCE_INTERVAL:
                    handler.pending_change = False
                    run_worker(ON_CHANGE_COMMAND)
        except KeyboardInterrupt:
            observer.stop()
            log("Watcher stopped by user.")
        observer.join()

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False


def run_polling() -> None:
    log("Watchdog is unavailable; using local polling for index updates.")
    last_state = get_md_files_state()
    last_change_time = 0.0
    pending_change = False
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_state = get_md_files_state()
            if current_state != last_state:
                last_state = current_state
                last_change_time = time.time()
                pending_change = True
                log("Detected local Markdown change.")
            if pending_change and time.time() - last_change_time >= DEBOUNCE_INTERVAL:
                pending_change = False
                run_worker(ON_CHANGE_COMMAND)
    except KeyboardInterrupt:
        log("Watcher stopped by user.")


if __name__ == "__main__":
    log(f"Starting Zephyr local-only watcher ({ON_CHANGE_COMMAND}). It never invokes an agent or network API.")
    run_watchdog() if HAS_WATCHDOG else run_polling()
