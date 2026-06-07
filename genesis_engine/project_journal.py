from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class Journal(ABC):
    """Interface for project journals (local file and future hosted implementations).

    Phase 1 will add HostedJournal that writes entries to the remote DB
    and re-ingests them into the dev namespace automatically.
    """

    @abstractmethod
    def append_entry(self, title: str, details: str, category: Optional[str] = None) -> None: ...

    @abstractmethod
    def read_log(self) -> str: ...

    @abstractmethod
    def list_entries(self) -> List[str]: ...


class ProjectJournal(Journal):
    """Local file-based journal. Appends structured entries to a markdown log file."""

    def __init__(self, path: str = "project_dev_log.md") -> None:
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("# Genesis Engine - Development Log\n\n", encoding="utf-8")

    def append_entry(self, title: str, details: str, category: Optional[str] = None) -> None:
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        header = f"## {title} — {category}" if category else f"## {title}"
        entry_text = (
            f"{header}\n\n"
            f"- **Date:** {timestamp}\n"
            f"- **Category:** {category or 'General'}\n\n"
            f"{details.strip()}\n\n"
        )
        self.path.write_text(self.path.read_text(encoding="utf-8") + entry_text, encoding="utf-8")

    def read_log(self) -> str:
        return self.path.read_text(encoding="utf-8")

    def update_section(self, section_title: str, content: str) -> None:
        original = self.read_log()
        section_header = f"## {section_title}"
        if section_header not in original:
            self.path.write_text(
                original + f"\n{section_header}\n\n{content.strip()}\n", encoding="utf-8"
            )
            return
        sections = original.split(section_header)
        before = sections[0]
        rest = section_header.join(sections[1:])
        after = rest.split("## ", 1)[1] if "## " in rest else ""
        updated = f"{before}{section_header}\n\n{content.strip()}\n\n{after}".strip() + "\n"
        self.path.write_text(updated, encoding="utf-8")

    def list_entries(self) -> List[str]:
        return [line for line in self.read_log().splitlines() if line.startswith("## ")]
