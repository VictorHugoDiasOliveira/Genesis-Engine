"""
Genesis Engine CLI — query the knowledge base from the terminal.

Reads genesis.yaml if present; falls back to local mode with knowledge/ directory.

Usage:
    python -m genesis_engine.cli query "your question"
    python -m genesis_engine.cli query "your question" --namespace dev --namespace external
    python -m genesis_engine.cli query "your question" -k 10
    python -m genesis_engine.cli read best-practices/clean-code
    python -m genesis_engine.cli namespaces
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_manager():
    sys.path.insert(0, str(ROOT))
    from genesis_engine.config import load_config
    from genesis_engine.rag import KnowledgeManager

    config = load_config(ROOT / "genesis.yaml")

    if config.is_hosted:
        # Phase 1: HostedVectorStore will be wired here.
        raise NotImplementedError(
            "Hosted mode is not yet implemented. Remove 'mode: hosted' from genesis.yaml "
            "or wait for Phase 1."
        )

    knowledge_dir = ROOT / config.knowledge_dir
    manager = KnowledgeManager()

    namespace_dirs = {
        "dev": knowledge_dir / "dev",
        "business": knowledge_dir / "business",
        "external": knowledge_dir / "external",
    }

    for name, path in namespace_dirs.items():
        if path.exists():
            if name == "external":
                manager.ingest_skill_namespace(name, str(path))
            else:
                manager.ingest_markdown_directory(name, str(path))

    return manager


def _knowledge_external(config_path: Path) -> Path:
    from genesis_engine.config import load_config
    config = load_config(config_path)
    return ROOT / config.knowledge_dir / "external"


def cmd_query(args: argparse.Namespace) -> None:
    manager = build_manager()
    namespaces = list(args.namespace) if args.namespace else None
    results = manager.search(args.query, k=args.k, namespaces=namespaces)

    found_any = False
    for namespace, items in results.items():
        relevant = [r for r in items if r.score >= args.min_score]
        if not relevant:
            continue
        found_any = True
        print(f"\n── {namespace} ──")
        for r in relevant:
            print(f"  {r.score:.4f}  {r.document.source}")

    if not found_any:
        print("No results found.")


def cmd_read(args: argparse.Namespace) -> None:
    external_dir = _knowledge_external(ROOT / "genesis.yaml")
    theme_path = external_dir / args.theme
    if not theme_path.exists():
        print(f"Theme not found: {args.theme}")
        print(f"Expected path: {theme_path}")
        sys.exit(1)

    md_files = sorted(theme_path.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found in: {args.theme}")
        sys.exit(1)

    print(f"\n══ {args.theme} ══\n")
    for md_file in md_files:
        relative = md_file.relative_to(theme_path)
        if str(relative) != "SKILL.md":
            print(f"── {relative} ──\n")
        print(md_file.read_text(encoding="utf-8"))
        print()


def cmd_namespaces(args: argparse.Namespace) -> None:
    manager = build_manager()
    namespaces = manager.list_namespaces()
    if not namespaces:
        print("No namespaces loaded.")
        return
    print("\nAvailable namespaces:")
    for ns in namespaces:
        print(f"  {ns}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="genesis",
        description="Genesis Engine — query the knowledge base",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    query_parser = subparsers.add_parser("query", help="Search the knowledge base")
    query_parser.add_argument("query", help="Search query")
    query_parser.add_argument(
        "--namespace", "-n",
        action="append",
        metavar="NS",
        help="Namespace(s) to search (repeatable). Defaults to all.",
    )
    query_parser.add_argument(
        "-k",
        type=int,
        default=5,
        metavar="N",
        help="Number of results per namespace (default: 5)",
    )
    query_parser.add_argument(
        "--min-score",
        type=float,
        default=0.10,
        metavar="SCORE",
        help="Minimum relevance score to show a result (default: 0.10)",
    )
    query_parser.set_defaults(func=cmd_query)

    read_parser = subparsers.add_parser("read", help="Read full content of an external theme")
    read_parser.add_argument(
        "theme",
        help="Theme path under knowledge/external/ (e.g. best-practices/clean-code)",
    )
    read_parser.set_defaults(func=cmd_read)

    ns_parser = subparsers.add_parser("namespaces", help="List available namespaces")
    ns_parser.set_defaults(func=cmd_namespaces)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
