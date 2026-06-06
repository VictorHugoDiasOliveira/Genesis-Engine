from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False


@dataclass
class Document:
    source: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    document: Document
    score: float


# — TF-IDF fallback store —

def _normalize_text(text: str) -> List[str]:
    words = re.findall(r"\w+", text.lower())
    return [word for word in words if len(word) > 1]


def _cosine_similarity(a: Counter, b: Counter) -> float:
    intersection = set(a.keys()) & set(b.keys())
    numerator = sum(a[token] * b[token] for token in intersection)
    sum_a = sum(v * v for v in a.values())
    sum_b = sum(v * v for v in b.values())
    denominator = math.sqrt(sum_a) * math.sqrt(sum_b)
    return numerator / denominator if denominator else 0.0


class SimpleVectorStore:
    def __init__(self) -> None:
        self.documents: List[Document] = []
        self.vectors: List[Counter] = []

    def add_documents(self, documents: Iterable[Document]) -> None:
        for document in documents:
            tokens = _normalize_text(document.content)
            self.documents.append(document)
            self.vectors.append(Counter(tokens))

    def similarity_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        query_vector = Counter(_normalize_text(query))
        scores: List[Tuple[int, float]] = [
            (i, _cosine_similarity(query_vector, v)) for i, v in enumerate(self.vectors)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [RetrievalResult(document=self.documents[i], score=s) for i, s in scores[:k]]


# — Semantic store (sentence-transformers) —

class SemanticVectorStore:
    """Dense vector store using sentence-transformers for semantic similarity."""

    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(self) -> None:
        import logging
        logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
        self._model = SentenceTransformer(self.MODEL_NAME, local_files_only=False)
        self.documents: List[Document] = []
        self._embeddings: Optional[np.ndarray] = None

    def add_documents(self, documents: Iterable[Document]) -> None:
        new_docs = list(documents)
        if not new_docs:
            return
        self.documents.extend(new_docs)
        new_embeddings = self._model.encode(
            [doc.content for doc in new_docs],
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        self._embeddings = (
            new_embeddings if self._embeddings is None
            else np.vstack([self._embeddings, new_embeddings])
        )

    def similarity_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        if not self.documents or self._embeddings is None:
            return []
        query_embedding = self._model.encode(
            [query], normalize_embeddings=True, show_progress_bar=False
        )
        scores = (self._embeddings @ query_embedding.T).flatten()
        top_k = int(min(k, len(self.documents)))
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            RetrievalResult(document=self.documents[i], score=float(scores[i]))
            for i in top_indices
        ]


def _create_store() -> SimpleVectorStore | SemanticVectorStore:
    if _SEMANTIC_AVAILABLE:
        return SemanticVectorStore()
    return SimpleVectorStore()


# — Knowledge base —

class RAGKnowledgeBase:
    def __init__(self, name: str) -> None:
        self.name = name
        self.store = _create_store()

    def ingest_document(self, source: str, content: str, metadata: Optional[Dict[str, str]] = None) -> None:
        document = Document(source=source, content=content, metadata=metadata or {})
        self.store.add_documents([document])

    def ingest_markdown_dir(self, directory: str) -> None:
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        for file_path in sorted(path.rglob("*.md")):
            source = str(file_path.relative_to(path))
            content = file_path.read_text(encoding="utf-8")
            self.ingest_document(source=source, content=content, metadata={"path": str(file_path)})

    def ingest_skill_namespace(self, directory: str) -> None:
        """Ingest each skill directory (anchored by SKILL.md) as a single document."""
        base = Path(directory)
        if not base.exists() or not base.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        for skill_md in sorted(base.rglob("SKILL.md")):
            skill_dir = skill_md.parent
            content = "\n\n".join(
                f.read_text(encoding="utf-8") for f in sorted(skill_dir.rglob("*.md"))
            )
            source = str(skill_dir.relative_to(base))
            self.ingest_document(source=source, content=content, metadata={"path": str(skill_dir), "type": "skill"})

    def search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        return self.store.similarity_search(query, k=k)


# — Manager —

class KnowledgeManager:
    def __init__(self) -> None:
        self.namespaces: Dict[str, RAGKnowledgeBase] = {}

    def add_namespace(self, name: str) -> RAGKnowledgeBase:
        if name not in self.namespaces:
            self.namespaces[name] = RAGKnowledgeBase(name=name)
        return self.namespaces[name]

    def search(self, query: str, k: int = 5, namespaces: Optional[List[str]] = None) -> Dict[str, List[RetrievalResult]]:
        selected = namespaces if namespaces is not None else list(self.namespaces.keys())
        return {
            ns: self.namespaces[ns].search(query, k=k)
            for ns in selected
            if ns in self.namespaces
        }

    def ingest_markdown_directory(self, namespace: str, directory: str) -> None:
        self.add_namespace(namespace).ingest_markdown_dir(directory)

    def ingest_skill_namespace(self, namespace: str, directory: str) -> None:
        self.add_namespace(namespace).ingest_skill_namespace(directory)

    def list_namespaces(self) -> List[str]:
        return sorted(self.namespaces.keys())
