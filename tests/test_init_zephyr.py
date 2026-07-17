import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_PATH = REPO_ROOT / "init-zephyr.py"


def load_init_module():
    spec = importlib.util.spec_from_file_location("zephyr_init", INIT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {INIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UpdateModeTests(unittest.TestCase):
    def test_update_preserves_personal_notes_and_config(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "Zephyr"
            (vault / "Capture").mkdir(parents=True)
            (vault / "Brain").mkdir()
            (vault / "System").mkdir()
            (vault / ".obsidian").mkdir()

            daily_log = vault / "Capture" / "2026-07-16.md"
            daily_log.write_text("personal daily log must survive", encoding="utf-8")
            private_note = vault / "Brain" / "Private Note.md"
            private_note.write_text("personal knowledge must survive", encoding="utf-8")
            config_path = vault / "System" / "config.json"
            config_path.write_text(json.dumps({"ai_model": "personal-model"}), encoding="utf-8")
            appearance_path = vault / ".obsidian" / "appearance.json"
            appearance_path.write_text(json.dumps({"customPreference": True}), encoding="utf-8")

            module = load_init_module()
            with patch.object(module, "DEFAULT_VAULT_DIR", str(vault)), patch.object(
                sys, "argv", ["init-zephyr.py", "--update"]
            ):
                module.main()

            self.assertEqual(daily_log.read_text(encoding="utf-8"), "personal daily log must survive")
            self.assertEqual(private_note.read_text(encoding="utf-8"), "personal knowledge must survive")
            self.assertEqual(json.loads(config_path.read_text(encoding="utf-8"))["ai_model"], "personal-model")
            self.assertTrue(json.loads(appearance_path.read_text(encoding="utf-8"))["customPreference"])
            self.assertEqual(
                (vault / "System" / "zephyr-worker.py").read_text(encoding="utf-8"),
                (REPO_ROOT / "System" / "zephyr-worker.py").read_text(encoding="utf-8"),
            )

    def test_update_requires_an_initialized_vault(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir) / "Zephyr"
            vault.mkdir()
            module = load_init_module()
            with patch.object(module, "DEFAULT_VAULT_DIR", str(vault)), patch.object(
                sys, "argv", ["init-zephyr.py", "--update"]
            ):
                with self.assertRaises(SystemExit):
                    module.main()


if __name__ == "__main__":
    unittest.main()
