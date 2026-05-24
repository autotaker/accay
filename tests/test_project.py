from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from accay.project import init_project, install_skills


class ProjectTests(unittest.TestCase):
    def test_init_project_creates_config_and_standard_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()

            result = init_project(root)

            self.assertIn(root / ".accay" / "config.yaml", result.created)
            self.assertTrue((root / "docs" / "acceptance" / "scenarios").is_dir())
            self.assertTrue((root / "docs" / "acceptance" / "components").is_dir())
            self.assertTrue((root / ".agents" / "skills").is_dir())

    def test_install_skills_creates_expected_skill_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            result = install_skills(root)

            self.assertEqual(4, len(result.created))
            self.assertTrue(
                (root / ".agents" / "skills" / "accay-acceptance-review" / "SKILL.md").is_file()
            )


if __name__ == "__main__":
    unittest.main()
