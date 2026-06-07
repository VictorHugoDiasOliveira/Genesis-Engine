from __future__ import annotations

from pathlib import Path
from typing import Optional

from genesis_engine.agent import AgentConnector, Message
from genesis_engine.config import GenesisConfig
from genesis_engine.rag import KnowledgeManager

_SYSTEM_PROMPT = (
    "You are a knowledgeable assistant with full access to the project's knowledge base. "
    "Answer the user's question based exclusively on the context provided. "
    "Be direct and specific. If the context does not contain enough information to answer "
    "confidently, say so — do not invent details. "
    "Format your answer clearly; use markdown lists or sections when it helps readability."
)

_MAX_CONTEXT_CHARS = 12_000


def run(
    question: str,
    manager: KnowledgeManager,
    config: GenesisConfig,
    namespaces: Optional[list[str]] = None,
    k: int = 5,
) -> None:
    """Query the RAG for context, then ask the LLM to answer the question."""
    results = manager.search(question, k=k, namespaces=namespaces)

    # Collect relevant documents above threshold, ordered by score
    scored_docs: list[tuple[float, str, str]] = []
    for namespace, items in results.items():
        for r in items:
            if r.score >= 0.10:
                scored_docs.append((r.score, namespace, r.document.content))

    scored_docs.sort(key=lambda x: x[0], reverse=True)

    if not scored_docs:
        print("No relevant context found in the knowledge base for that question.")
        return

    # Build context block, capped to avoid exceeding model context
    context_lines: list[str] = []
    total_chars = 0
    sources_used: list[str] = []

    for _score, namespace, content in scored_docs:
        if total_chars >= _MAX_CONTEXT_CHARS:
            break
        entry = f"[{namespace}]\n{content}"
        context_lines.append(entry)
        total_chars += len(entry)

    context_block = "\n\n---\n\n".join(context_lines)

    messages = [
        Message(role="system", content=_SYSTEM_PROMPT),
        Message(
            role="user",
            content=(
                f"Context from the knowledge base:\n\n{context_block}\n\n"
                f"---\n\nQuestion: {question}"
            ),
        ),
    ]

    connector = AgentConnector(config)

    print()
    for chunk in connector.stream(messages, task="analysis"):
        print(chunk, end="", flush=True)
    print("\n")
