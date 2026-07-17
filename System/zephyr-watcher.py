import os
import sys
import time
import subprocess
from datetime import datetime

# Setup directories relative to this script
SYSTEM_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DIR = os.path.dirname(SYSTEM_DIR)
CAPTURE_DIR = os.path.join(VAULT_DIR, "Capture")
BRAIN_DIR = os.path.join(VAULT_DIR, "Brain")
WORKER_PATH = os.path.join(SYSTEM_DIR, "zephyr-worker.py")

# Configurations
DEBOUNCE_INTERVAL = 2.0  # seconds to wait after last change before triggering
POLL_INTERVAL = 2.0      # seconds between polling checks (if in polling mode)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [Watcher] {msg}")

def run_worker(mode="index"):
    log(f"Triggering zephyr-worker.py {mode}...")
    try:
        result = subprocess.run(
            [sys.executable, WORKER_PATH, mode],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.stdout:
            for line in result.stdout.splitlines():
                if line.strip():
                    print(f"  [Worker] {line}")
        if result.stderr:
            for line in result.stderr.splitlines():
                if line.strip():
                    print(f"  [Worker-Error] {line}")
        log("Worker finished successfully.")
    except Exception as e:
        log(f"Error running worker: {e}")

# ==============================================================================
# 1. Watchdog Event Handler Mode (If watchdog is installed)
# ==============================================================================
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ZephyrHandler(FileSystemEventHandler):
        def __init__(self):
            super().__init__()
            self.last_change_time = 0.0
            self.pending_change = False
            self.trigger_mode = "index"

        def on_any_event(self, event):
            # Only monitor markdown file modifications/creations/deletions
            if event.is_directory or not event.src_path.endswith(".md"):
                return
            if os.path.basename(event.src_path) == "Home.md":
                return
            
            # Record change time
            self.last_change_time = time.time()
            self.pending_change = True
            
            fname = os.path.basename(event.src_path)
            is_capture_md = (
                event.src_path.replace("\\", "/").startswith(CAPTURE_DIR.replace("\\", "/"))
                and not fname.endswith(" -- draft.md")
                and event.event_type in {"created", "modified"}
            )
            
            if is_capture_md:
                self.trigger_mode = "triage"
                log(f"Detected change (triage needed): {fname} ({event.event_type})")
            else:
                log(f"Detected change (index needed): {fname} ({event.event_type})")

    def run_watchdog():
        log("Watchdog library detected. Starting event-driven file watcher...")
        handler = ZephyrHandler()
        observer = Observer()
        
        # Monitor Capture and Brain
        if os.path.exists(CAPTURE_DIR):
            observer.schedule(handler, path=CAPTURE_DIR, recursive=False)
            log(f"Monitoring Capture directory: {CAPTURE_DIR}")
        if os.path.exists(BRAIN_DIR):
            observer.schedule(handler, path=BRAIN_DIR, recursive=False)
            log(f"Monitoring Brain directory: {BRAIN_DIR}")
            
        observer.start()
        try:
            while True:
                time.sleep(0.5)
                # Debounce logic
                if handler.pending_change and (time.time() - handler.last_change_time >= DEBOUNCE_INTERVAL):
                    handler.pending_change = False
                    mode = handler.trigger_mode
                    handler.trigger_mode = "index"
                    run_worker(mode)
        except KeyboardInterrupt:
            observer.stop()
            log("Watcher stopped by user.")
        observer.join()

    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False

# ==============================================================================
# 2. Polling Mode (Zero-dependency fallback)
# ==============================================================================
def get_md_files_state():
    state = {}
    for dpath in [CAPTURE_DIR, BRAIN_DIR]:
        if not os.path.exists(dpath):
            continue
        for fname in os.listdir(dpath):
            if not fname.endswith(".md") or fname == "Home.md":
                continue
            fpath = os.path.join(dpath, fname)
            try:
                state[fpath] = os.path.getmtime(fpath)
            except Exception:
                # File might be deleted/locked during scan
                pass
    return state

def run_polling():
    log("Watchdog library not installed. Starting fallback polling watcher...")
    log(f"Monitoring directories: Capture/ & Brain/ (polling interval: {POLL_INTERVAL}s)")
    
    last_state = get_md_files_state()
    last_change_time = 0.0
    pending_change = False
    triage_needed = False
    
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            current_state = get_md_files_state()
            
            # Detect changes (added, modified, or deleted files)
            changes = []
            
            # Check for modified or new files
            for path, mtime in current_state.items():
                fname = os.path.basename(path)
                is_add_or_mod = False
                if path not in last_state:
                    changes.append(f"Added {fname}")
                    is_add_or_mod = True
                elif last_state[path] != mtime:
                    changes.append(f"Modified {fname}")
                    is_add_or_mod = True
                
                if is_add_or_mod:
                    is_capture_md = (
                        path.replace("\\", "/").startswith(CAPTURE_DIR.replace("\\", "/"))
                        and not fname.endswith(" -- draft.md")
                    )
                    if is_capture_md:
                        triage_needed = True
                    
            # Check for deleted files
            for path in last_state:
                if path not in current_state:
                    changes.append(f"Deleted {os.path.basename(path)}")
                    
            if changes:
                last_change_time = time.time()
                last_state = current_state
                if not pending_change:
                    pending_change = True
                    log(f"Detected changes: {', '.join(changes)}")
                    
            # Debounce logic
            if pending_change and (time.time() - last_change_time >= DEBOUNCE_INTERVAL):
                pending_change = False
                mode = "triage" if triage_needed else "index"
                triage_needed = False
                run_worker(mode)
                
    except KeyboardInterrupt:
        log("Watcher stopped by user.")

# ==============================================================================
# Main Entry Point
# ==============================================================================
if __name__ == "__main__":
    log("Starting Zephyr File Watcher...")
    log(f"Vault Root: {VAULT_DIR}")
    
    if HAS_WATCHDOG:
        run_watchdog()
    else:
        run_polling()
