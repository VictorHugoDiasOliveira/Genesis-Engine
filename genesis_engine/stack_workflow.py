from __future__ import annotations

from pathlib import Path

from genesis_engine.agent import AgentConnector, Message
from genesis_engine.config import GenesisConfig
from genesis_engine.project_journal import ProjectJournal
from genesis_engine.rag import KnowledgeManager

_SYSTEM_PROMPT = (
    "You are a senior software architect. Given a project's business context and the user's "
    "technology preferences, produce a comprehensive, opinionated tech stack decision document. "
    "Be specific: name exact libraries and versions where relevant. Explain WHY each choice fits "
    "this project — tie every decision to a business or technical requirement from the context. "
    "Flag trade-offs honestly. Format as markdown with clear sections."
)

_SECTIONS = [
    "## Overview\n(One paragraph summarising the project and the guiding architectural principles behind the stack choices.)",
    "## Backend\n(Language, framework, database, ORM, migrations, auth, background jobs, logging.)",
    "## Frontend\n(Framework, styling, state management, API communication.)",
    "## Infrastructure & DevOps\n(Containerisation, CI/CD, hosting, environment management.)",
    "## Key Trade-offs & Risks\n(What was considered but rejected, and why. What risks the chosen stack introduces.)",
    "## Developer Setup\n(Minimal steps to get a new developer running locally.)",
]


def _build_context(manager: KnowledgeManager, preferences: str) -> str:
    results = manager.search(
        "product features MVP architecture target audience business model",
        k=6,
        namespaces=["business"],
    )
    chunks: list[str] = []
    for namespace, items in results.items():
        for r in items:
            if r.score >= 0.10:
                chunks.append(f"[{namespace}/{r.document.source}]\n{r.document.content}")

    context = "\n\n---\n\n".join(chunks)
    if preferences:
        context += f"\n\n---\n\n[User preferences / constraints]\n{preferences}"
    return context


def run(preferences: str, manager: KnowledgeManager, config: GenesisConfig, base_dir: Path) -> None:
    """Generate a stack decision document grounded in the project's business context.

    Queries the business RAG for context, incorporates user preferences,
    and produces a markdown document saved to knowledge/dev/stack.md.
    """
    connector = AgentConnector(config)
    dev_dir = base_dir / config.knowledge_dir / "dev"
    dev_dir.mkdir(parents=True, exist_ok=True)

    provider = connector._resolve_provider("analysis")
    print(f"\nGenesis Engine — Stack Advisor")
    print(f"Provider   : {provider}")
    if preferences:
        print(f"Preferences: {preferences}")
    print()

    context = _build_context(manager, preferences)

    sections_prompt = "\n".join(_SECTIONS)
    messages = [
        Message(role="system", content=_SYSTEM_PROMPT),
        Message(
            role="user",
            content=(
                f"Project context:\n\n{context}\n\n"
                f"---\n\n"
                f"Generate the full tech stack decision document covering these sections:\n\n"
                f"{sections_prompt}\n\n"
                f"Be concrete. Every choice must be justified by a specific business or technical "
                f"need visible in the context above."
            ),
        ),
    ]

    print("Generating stack document ", end="", flush=True)
    content = connector.chat(messages, task="analysis")
    print("done\n")

    out_file = dev_dir / "stack.md"
    out_file.write_text(content, encoding="utf-8")
    print(f"Saved to {out_file.relative_to(base_dir)}\n")
    print(content)
    print()

    journal_path = base_dir / "project_dev_log.md"
    if journal_path.exists():
        journal = ProjectJournal(str(journal_path))
        journal.append_entry(
            title="Stack decision document generated",
            details=(
                f"Tech stack document generated via Genesis Engine (provider: {provider}).\n\n"
                f"Saved to knowledge/dev/stack.md.\n\n"
                + (f"User preferences provided: {preferences}" if preferences else "No explicit preferences — LLM chose based on business context alone.")
            ),
            category="Architecture",
        )

    # Automatically find and install relevant skills for the chosen stack
    print("─" * 60)
    print("Searching skills.sh for stack technologies...")
    print("─" * 60)
    from genesis_engine.skill_workflow import run as install_skills
    installed = install_skills(stack_content=content, config=config, base_dir=base_dir)

    if installed:
        print(f"\n{len(installed)} skill(s) installed and ingested into knowledge/external/.")
    else:
        print("\nNo skills installed (npx unavailable or no matching skills found).")
    print()
