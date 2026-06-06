from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional


class ProjectJournal:
    def __init__(self, path: str = "project_dev_log.md") -> None:
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("# Genesis Engine - Development Log\n\n", encoding="utf-8")

    def append_entry(self, title: str, details: str, category: Optional[str] = None) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        header = f"## {title}"
        if category:
            header = f"## {title} — {category}"

        entry_text = f"{header}\n\n" \
            f"- **Date:** {timestamp}\n" \
            f"- **Category:** {category or 'General'}\n\n" \
            f"{details.strip()}\n\n"

        self.path.write_text(self.path.read_text(encoding="utf-8") + entry_text, encoding="utf-8")

    def read_log(self) -> str:
        return self.path.read_text(encoding="utf-8")

    def update_section(self, section_title: str, content: str) -> None:
        original = self.read_log()
        section_header = f"## {section_title}"
        if section_header not in original:
            self.path.write_text(original + f"\n{section_header}\n\n{content.strip()}\n", encoding="utf-8")
            return

        sections = original.split(section_header)
        before = sections[0]
        rest = section_header.join(sections[1:])
        next_section = "## "
        if next_section in rest:
            after = rest.split(next_section, 1)[1]
        else:
            after = ""
        updated = f"{before}{section_header}\n\n{content.strip()}\n\n{after}".strip() + "\n"
        self.path.write_text(updated, encoding="utf-8")

    def list_entries(self) -> List[str]:
        content = self.read_log()
        return [line for line in content.splitlines() if line.startswith("## ")]
