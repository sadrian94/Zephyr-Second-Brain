import json
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "System" / "skills"


class SkillContractTests(unittest.TestCase):
    def test_every_skill_declares_automation_contract(self):
        skill_paths = sorted(SKILLS_DIR.glob("*.md"))
        self.assertEqual(len(skill_paths), 7)
        seen_ids = set()

        for path in skill_paths:
            content = path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"), path.name)
            _, raw_frontmatter, _ = content.split("---", 2)
            frontmatter = yaml.safe_load(raw_frontmatter)
            for key in ("id", "trigger", "automation", "safe_to_schedule", "writes"):
                self.assertIn(key, frontmatter, f"{path.name}: missing {key}")
            self.assertNotIn(frontmatter["id"], seen_ids)
            seen_ids.add(frontmatter["id"])
            self.assertIn(frontmatter["automation"], {"observe", "draft", "commit"})
            self.assertIsInstance(frontmatter["safe_to_schedule"], bool)
            self.assertIsInstance(frontmatter["writes"], list)
            self.assertTrue(set(frontmatter["writes"]).issubset({"System", "Capture"}))
            if frontmatter["automation"] == "observe":
                self.assertEqual(frontmatter["writes"], ["System"])
            if frontmatter["automation"] == "draft":
                self.assertEqual(frontmatter["writes"], ["Capture"])

    def test_automation_example_is_safe_by_default(self):
        config = json.loads((REPO_ROOT / "System" / "automation.example.json").read_text(encoding="utf-8"))
        self.assertEqual(config["on_change"], "refresh")
        self.assertFalse(config["agent_drafts"]["enabled"])
        self.assertFalse(config["external_delivery"]["enabled"])
        skill_ids = set()
        for path in SKILLS_DIR.glob("*.md"):
            _, raw_frontmatter, _ = path.read_text(encoding="utf-8").split("---", 2)
            skill_ids.add(yaml.safe_load(raw_frontmatter)["id"])
        self.assertTrue(set(config["agent_drafts"]["allowed_skills"]).issubset(skill_ids))

    def test_source_template_is_a_proposal_not_durable_knowledge(self):
        content = (REPO_ROOT / "System" / "templates" / "source-note.md").read_text(encoding="utf-8")
        _, raw_frontmatter, _ = content.split("---", 2)
        frontmatter = yaml.safe_load(raw_frontmatter)
        self.assertEqual(frontmatter["suggested_type"], "note")
        self.assertEqual(frontmatter["triage_status"], "proposed")
        self.assertNotIn("type", frontmatter)


if __name__ == "__main__":
    unittest.main()
