from __future__ import annotations

import sys
from pathlib import Path

from genesis_engine.agent import AgentConnector, Message
from genesis_engine.config import GenesisConfig
from genesis_engine.project_journal import ProjectJournal

_SYSTEM_PROMPT = (
    "You are a senior startup advisor and business strategist with deep experience "
    "in product development and go-to-market strategy. "
    "Write clear, specific, and actionable business documentation in markdown. "
    "Be direct — avoid generic advice. Every recommendation must be tailored to the project."
)

# Each section: (filename, topic, guiding questions)
_SECTIONS: list[tuple[str, str, str]] = [
    (
        "vision",
        "Vision, Mission, and Values",
        "Define the mission statement (what we do and for whom), the long-term vision "
        "(where we want to be in 5 years), and 3–5 core values that will guide every decision.",
    ),
    (
        "market",
        "Target Market and Competitive Analysis",
        "Identify the primary target audience (demographics, behaviors, pain points). "
        "Estimate the addressable market. List the main competitors and explain how this "
        "project differentiates itself from each.",
    ),
    (
        "product",
        "Product Definition and MVP Scope",
        "List the 5–8 core features of the product. Define the MVP — the smallest version "
        "that delivers real value. Outline a 3-phase product roadmap (MVP, Growth, Scale).",
    ),
    (
        "business-model",
        "Business Model and Monetization",
        "Describe the revenue streams (freemium, subscription, ads, marketplace, etc.). "
        "Propose a pricing strategy with specific tiers if applicable. "
        "Estimate a realistic monetization timeline.",
    ),
    (
        "okrs",
        "First-Quarter OKRs",
        "Define 3 Objectives for the first quarter (Q1). "
        "For each Objective, write 2–3 measurable Key Results. "
        "Focus on validation and early traction — not scale.",
    ),
]


def run(idea: str, config: GenesisConfig, base_dir: Path) -> None:
    """Run the business planning workflow for a project idea.

    Generates five business plan sections via the configured LLM and saves
    each as a markdown file under knowledge/business/. Logs the session to
    project_dev_log.md.
    """
    connector = AgentConnector(config)
    business_dir = base_dir / config.knowledge_dir / "business"
    business_dir.mkdir(parents=True, exist_ok=True)

    provider = connector._resolve_provider("business")
    print(f"\nGenesis Engine — Business Planning")
    print(f"Provider : {provider}")
    print(f"Project  : {idea}")
    print(f"Output   : {business_dir.relative_to(base_dir)}/\n")

    generated: list[str] = []

    for filename, topic, guidance in _SECTIONS:
        print(f"  [{len(generated) + 1}/{len(_SECTIONS)}] {topic} ...", end=" ", flush=True)

        messages = [
            Message(role="system", content=_SYSTEM_PROMPT),
            Message(
                role="user",
                content=(
                    f"Project: {idea}\n\n"
                    f"Write the '{topic}' section of the business plan.\n\n"
                    f"{guidance}\n\n"
                    f"Format: markdown with a top-level heading and clear subsections."
                ),
            ),
        ]

        content = connector.chat(messages, task="business")
        out_file = business_dir / f"{filename}.md"
        out_file.write_text(content, encoding="utf-8")
        generated.append(filename)
        print("done")

    # Log the session
    journal_path = base_dir / "project_dev_log.md"
    if journal_path.exists():
        journal = ProjectJournal(str(journal_path))
        journal.append_entry(
            title="Business Plan Generated",
            details=(
                f"Initial business plan created via Genesis Engine (provider: {provider}).\n\n"
                f"Idea: {idea}\n\n"
                f"Sections saved to knowledge/business/:\n"
                + "\n".join(f"- {f}.md" for f in generated)
            ),
            category="Task",
        )

    print(f"\nDone. {len(generated)} sections saved to {business_dir.relative_to(base_dir)}/")
    print("Run `python -m genesis_engine.cli query \"<question>\" --namespace business` to query the plan.\n")
