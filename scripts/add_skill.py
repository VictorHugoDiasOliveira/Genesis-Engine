"""
Add a skill from .agents/skills/ into the RAG knowledge base.

Each skill is placed in its own subdirectory under knowledge/external/<theme>/<skill-name>/
to avoid overwriting files when multiple skills share the same theme.

Usage:
    python scripts/add_skill.py <skill-name> <theme>

Arguments:
    skill-name  Directory name under .agents/skills/
    theme       Subdirectory under knowledge/external/ (e.g. best-practices, languages/python)

Example:
    python scripts/add_skill.py clean-code best-practices
    python scripts/add_skill.py python-best-practices languages/python
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
KNOWLEDGE_EXTERNAL = ROOT / "knowledge" / "external"


def add_skill(skill_name: str, theme: str) -> None:
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        print(f"Error: skill '{skill_name}' not found in {SKILLS_DIR}")
        sys.exit(1)

    dest_dir = KNOWLEDGE_EXTERNAL / theme / skill_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for src_file in sorted(skill_dir.rglob("*.md")):
        relative = src_file.relative_to(skill_dir)
        dest_file = dest_dir / relative
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        copied.append(str(dest_file.relative_to(ROOT)))

    if not copied:
        print(f"Warning: no markdown files found in skill '{skill_name}'")
        return

    print(f"Skill '{skill_name}' added to knowledge/external/{theme}/{skill_name}/")
    for path in copied:
        print(f"  + {path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    add_skill(skill_name=sys.argv[1], theme=sys.argv[2])
