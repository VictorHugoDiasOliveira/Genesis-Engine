import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from genesis_engine.rag import KnowledgeManager


def main() -> None:
    manager = KnowledgeManager()
    manager.ingest_markdown_directory("dev", "knowledge/dev")
    manager.ingest_markdown_directory("business", "knowledge/business")
    manager.ingest_markdown_directory("external", "knowledge/external")

    query = "How should Genesis Engine use RAG to support development?"
    results = manager.search(query, k=5)

    for namespace, items in results.items():
        print(f"\n=== Namespace: {namespace}\n")
        for result in items:
            print(f"- {result.document.source} (score={result.score:.4f})")


if __name__ == "__main__":
    main()
