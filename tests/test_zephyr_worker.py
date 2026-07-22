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


class LifecycleSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault = Path(self.temp_dir.name)
        self.module = load_worker_module()
        for name in ("Capture", "Active", "Brain", "Archive", "System"):
            (self.vault / name).mkdir()
        self.module.VAULT_DIR = self.vault
        self.module.CAPTURE_DIR = self.vault / "Capture"
        self.module.ACTIVE_DIR = self.vault / "Active"
        self.module.BRAIN_DIR = self.vault / "Brain"
        self.module.ARCHIVE_DIR = self.vault / "Archive"
        self.module.SYSTEM_DIR = self.vault / "System"
        self.module.INDEX_PATH = self.vault / "System" / "index.json"
        self.module.STATUS_PATH = self.vault / "System" / "status.json"
        self.module.CONTENT_DIRS = (
            self.module.CAPTURE_DIR,
            self.module.ACTIVE_DIR,
            self.module.BRAIN_DIR,
            self.module.ARCHIVE_DIR,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_project(self, folder, status="active"):
        path = self.vault / folder / "Example.md"
        path.write_text(
            f"---\ntype: project\nstatus: {status}\npriority: medium\n"
            "deadline: 2026-08-01\narea: '[[Work]]'\ntags: [project]\n---\n\nBody stays intact.\n",
            encoding="utf-8",
        )
        return path

    def test_yaml_parser_preserves_nested_values_and_body(self):
        frontmatter, body = self.module.parse_frontmatter(
            "---\ntype: note\ntags: [one, two]\nmetadata:\n  quoted: 'yes: please'\n---\n\nBody\n"
        )
        self.assertEqual(frontmatter["metadata"]["quoted"], "yes: please")
        self.assertEqual(frontmatter["tags"], ["one", "two"])
        self.assertEqual(body, "Body\n")

    def test_activation_requires_approval_and_dry_run_keeps_source(self):
        source = self._write_project("Capture")
        with self.assertRaises(self.module.CommandError):
            self.module.activate(str(source), approve=False, dry_run=False)
        self.module.activate(str(source), approve=True, dry_run=True)
        self.assertTrue(source.exists())
        self.assertFalse((self.vault / "Active" / "Example.md").exists())

    def test_activation_and_completed_archive_are_explicit_and_body_safe(self):
        source = self._write_project("Capture")
        self.module.activate(str(source), approve=True, dry_run=False)
        active = self.vault / "Active" / "Example.md"
        self.assertTrue(active.exists())
        self.assertFalse(source.exists())
        self.assertIn("Body stays intact.", active.read_text(encoding="utf-8"))
        with self.assertRaises(self.module.CommandError):
            self.module.archive(str(active), approve=True, force=False, dry_run=False)
        active.write_text(active.read_text(encoding="utf-8").replace("status: active", "status: completed"), encoding="utf-8")
        self.module.archive(str(active), approve=True, force=False, dry_run=False)
        self.assertTrue((self.vault / "Archive" / "Example.md").exists())

    def test_invalid_project_is_not_moved(self):
        source = self.vault / "Capture" / "Incomplete.md"
        source.write_text("---\ntype: project\nstatus: active\n---\n\nKeep me.\n", encoding="utf-8")
        with self.assertRaises(self.module.CommandError):
            self.module.activate(str(source), approve=True, dry_run=False)
        self.assertTrue(source.exists())
        self.assertFalse((self.vault / "Active" / "Incomplete.md").exists())


if __name__ == "__main__":
    unittest.main()
