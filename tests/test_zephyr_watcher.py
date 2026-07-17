import importlib.util
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


REPO_ROOT = Path(__file__).resolve().parents[1]
WATCHER_PATH = REPO_ROOT / "System" / "zephyr-watcher.py"


def load_watcher_module():
    spec = importlib.util.spec_from_file_location("zephyr_watcher", WATCHER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {WATCHER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WatcherWorkerInvocationTests(unittest.TestCase):
    def test_run_worker_uses_index_mode(self):
        module = load_watcher_module()
        completed = MagicMock(stdout="", stderr="", returncode=0)

        with patch.object(module.subprocess, "run", return_value=completed) as run:
            module.run_worker()

        run.assert_called_once_with(
            [module.sys.executable, module.WORKER_PATH, "index"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
