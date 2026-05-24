from __future__ import annotations

from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path


DEFAULT_CONFIG = """docs_root: docs/acceptance

skills:
  install_dir: .agents/skills

language:
  verifies: ja
  reports: ja

junit:
  paths:
    - reports/python-junit.xml
    - reports/frontend-junit.xml

regression:
  accepted_failed: fail
  accepted_error: fail
  accepted_missing: fail
  accepted_skipped: fail
  non_accepted_failed: warning
  unmapped: info

reports:
  html_dir: .accay/reports/html
  markdown_dir: .accay/reports/markdown
"""


STANDARD_DIRS = [
    "docs/acceptance/scenarios",
    "docs/acceptance/sequences",
    "docs/acceptance/traces",
    "docs/acceptance/components",
    ".accay/templates",
    ".accay/runs",
    ".accay/reports/html",
    ".accay/reports/markdown",
    ".accay/generated",
    ".accay/cache",
    ".agents/skills",
]


SKILL_NAMES = [
    "accay-interface-semantics",
    "accay-desk-debugging",
    "accay-acceptance-review",
    "accay-acceptance-report",
]


@dataclass
class ProjectChange:
    created: list[Path] = field(default_factory=list)
    existing: list[Path] = field(default_factory=list)


def init_project(root: Path) -> ProjectChange:
    root = root.resolve()
    change = ProjectChange()

    for relative in STANDARD_DIRS:
        path = root / relative
        if path.exists():
            change.existing.append(path)
            continue
        path.mkdir(parents=True, exist_ok=True)
        change.created.append(path)

    config = root / ".accay" / "config.yaml"
    if config.exists():
        change.existing.append(config)
    else:
        config.write_text(DEFAULT_CONFIG, encoding="utf-8")
        change.created.append(config)

    return change


def install_skills(root: Path) -> ProjectChange:
    root = root.resolve()
    change = ProjectChange()
    install_dir = root / ".agents" / "skills"
    install_dir.mkdir(parents=True, exist_ok=True)

    for skill_name in SKILL_NAMES:
        destination = install_dir / skill_name
        skill_file = destination / "SKILL.md"
        if skill_file.exists():
            change.existing.append(skill_file)
            continue
        destination.mkdir(parents=True, exist_ok=True)
        skill_file.write_text(_read_skill_template(skill_name), encoding="utf-8")
        change.created.append(skill_file)

    return change


def _read_skill_template(skill_name: str) -> str:
    skill_path = resources.files("accay").joinpath("templates", "skills", skill_name, "SKILL.md")
    return skill_path.read_text(encoding="utf-8")
