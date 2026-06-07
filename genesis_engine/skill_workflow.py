from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from genesis_engine.agent import AgentConnector, Message
from genesis_engine.config import GenesisConfig
from genesis_engine.project_journal import ProjectJournal

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
_SKILL_REF = re.compile(r"([a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+)")

_EXTRACT_PROMPT = """\
You are a developer tool. Return ONLY a valid JSON array — no markdown, no explanation.

Given the tech stack document below, identify the key technologies that would benefit from
external best-practice skills from skills.sh.

For each technology return an object with:
  "query"  — short search term for `npx skills find` (e.g. "fastapi python REST API")
  "theme"  — knowledge/external/ subdirectory. Use one of:
               best-practices/  languages/python/  languages/javascript/
               infra/  database/  testing/  agent-skills/
  "name"   — short label for logging (e.g. "FastAPI")

Rules:
- Maximum 6 items. Focus on the most impactful technologies.
- Skip generic items (Git, GitHub, HTTP, JSON).
- Prefer specific frameworks over broad languages.

Return a JSON array only.
"""


def _strip_ansi(text: str) -> str:
    return _ANSI_ESCAPE.sub("", text)


def _parse_top_skill(output: str) -> str | None:
    """Extract the top-ranked owner/repo@skill-name from `npx skills find` output.

    Skips the generic placeholder that skills.sh prints in the header:
    'Install with npx skills add <owner/repo@skill>'
    """
    clean = _strip_ansi(output)
    for match in _SKILL_REF.finditer(clean):
        ref = match.group(1)
        if ref != "owner/repo@skill":
            return ref
    return None


def _extract_queries(stack_content: str, connector: AgentConnector) -> list[dict]:
    messages = [
        Message(role="system", content="You are a developer tool. Return only valid JSON, no markdown."),
        Message(role="user", content=f"{_EXTRACT_PROMPT}\n\nStack document:\n{stack_content}"),
    ]
    response = connector.chat(messages, task="analysis")
    match = re.search(r"\[.*\]", response, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def _find_skill(query: str) -> str | None:
    """Run `npx skills find <query>` and return the top skill reference."""
    try:
        result = subprocess.run(
            ["npx", "skills", "find", query],
            capture_output=True, text=True, timeout=30,
        )
        return _parse_top_skill(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def _install_skill(skill_ref: str, base_dir: Path) -> bool:
    """Run `npx skills add <ref>` from base_dir. Returns True on success."""
    try:
        result = subprocess.run(
            ["npx", "skills", "add", skill_ref],
            capture_output=True, text=True, timeout=60, cwd=str(base_dir),
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _ingest_skill(skill_name: str, theme: str, base_dir: Path) -> bool:
    """Copy skill markdown from .agents/skills/<name>/ to knowledge/external/<theme>/<name>/."""
    skill_dir = base_dir / ".agents" / "skills" / skill_name
    if not skill_dir.exists():
        return False

    dest_dir = base_dir / "knowledge" / "external" / theme / skill_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for src in sorted(skill_dir.rglob("*.md")):
        dest = dest_dir / src.relative_to(skill_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied += 1

    return copied > 0


def run(
    stack_content: str,
    config: GenesisConfig,
    base_dir: Path,
) -> list[str]:
    """Find, install, and ingest skills for each technology in the stack document.

    Returns the list of skill names successfully installed.
    """
    connector = AgentConnector(config)

    print("\nExtracting technologies from stack document...", end=" ", flush=True)
    queries = _extract_queries(stack_content, connector)
    if not queries:
        print("no technologies found.")
        return []
    print(f"{len(queries)} technologies identified.\n")

    installed: list[str] = []

    for item in queries:
        query = item.get("query", "")
        theme = item.get("theme", "best-practices").rstrip("/")
        name = item.get("name", query)

        print(f"  [{name}]", end=" ", flush=True)

        skill_ref = _find_skill(query)
        if not skill_ref:
            print("no skill found — skipping")
            continue

        skill_name = skill_ref.split("@")[-1]
        print(f"→ {skill_ref}", end=" ... ", flush=True)

        if not _install_skill(skill_ref, base_dir):
            print("install failed")
            continue

        if not _ingest_skill(skill_name, theme, base_dir):
            print("ingest failed")
            continue

        installed.append(skill_name)
        print("done")

    if installed:
        journal_path = base_dir / "project_dev_log.md"
        if journal_path.exists():
            journal = ProjectJournal(str(journal_path))
            journal.append_entry(
                title=f"Skills auto-installed from stack document",
                details=(
                    f"Genesis Engine automatically found and installed {len(installed)} skill(s) "
                    f"based on the generated stack document.\n\n"
                    + "\n".join(f"- {s}" for s in installed)
                    + "\n\nAll skills ingested into knowledge/external/."
                ),
                category="Implementation",
            )

    return installed
