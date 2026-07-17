import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = REPO_ROOT / "System" / "zephyr-worker.py"


def load_worker_module():
    spec = importlib.util.spec_from_file_location("zephyr_worker", WORKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {WORKER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InboxEligibilityTests(unittest.TestCase):
    def test_find_eligible_inbox_notes_excludes_typed_reviewed_and_drafts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            capture = Path(temp_dir) / "Capture"
            capture.mkdir()
            (capture / "Raw thought.md").write_text("A raw idea", encoding="utf-8")
            (capture / "Typed.md").write_text(
                '---\ntype: "note"\n---\n\nAlready handled', encoding="utf-8"
            )
            (capture / "Needs review.md").write_text(
                '---\ntriage_status: "needs_review"\n---\n\nAmbiguous', encoding="utf-8"
            )
            (capture / "Proposal -- draft.md").write_text("A draft", encoding="utf-8")
            (capture / "Home.md").write_text("Dashboard", encoding="utf-8")

            module = load_worker_module()
            setattr(module, "CAPTURE_DIR", str(capture))

            eligible = module.find_eligible_inbox_notes()

            self.assertEqual([Path(path).name for path in eligible], ["Raw thought.md"])


class WorkerModeTests(unittest.TestCase):
    def test_fast_mode_runs_only_index_maintenance(self):
        module = load_worker_module()

        with patch.object(module, "compile_index") as compile_index, patch.object(
            module, "heal_links"
        ) as heal_links, patch.object(module, "sync_git") as sync_git:
            exit_code = module.run_mode("fast")

        self.assertEqual(exit_code, 0)
        compile_index.assert_called_once_with()
        heal_links.assert_called_once_with()
        sync_git.assert_not_called()

    def test_sync_mode_only_runs_git_sync(self):
        module = load_worker_module()

        with patch.object(module, "compile_index") as compile_index, patch.object(
            module, "heal_links"
        ) as heal_links, patch.object(module, "sync_git") as sync_git:
            exit_code = module.run_mode("sync")

        self.assertEqual(exit_code, 0)
        sync_git.assert_called_once_with()
        compile_index.assert_not_called()
        heal_links.assert_not_called()


if __name__ == "__main__":
    unittest.main()
