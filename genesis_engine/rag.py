from __future__ import annotations

import hashlib
import math
import pickle
import re
from abc import ABC, abstractmethod
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


# — Abstract interface —

class VectorStore(ABC):
    """Interface for all vector store backends (local and hosted).

    Concrete implementations: SimpleVectorStore (TF-IDF, no deps),
    SemanticVectorStore (nomic embeddings, local cache).
    Phase 1 will add HostedVectorStore (Supabase pgvector or Pinecone).
    """

    @abstractmethod
    def add_documents(self, documents: Iterable[Document]) -> None: ...

    @abstractmethod
    def similarity_search(self, query: str, k: int = 5) -> List[RetrievalResult]: ...


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


class SimpleVectorStore(VectorStore):
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


# — Chunking helpers —

_CHUNK_SIZE = 1000    # characters (~250 tokens, safe for all embedding models)
_CHUNK_OVERLAP = 100  # characters of overlap between consecutive chunks


def _chunk_text(text: str) -> List[str]:
    """Split text into overlapping character-level chunks."""
    if len(text) <= _CHUNK_SIZE:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + _CHUNK_SIZE])
        start += _CHUNK_SIZE - _CHUNK_OVERLAP
    return chunks


# — Semantic store (sentence-transformers + chunking + disk cache) —

# Cache lives under .cache/rag_embeddings/ (already gitignored via .cache/)
_CACHE_DIR = Path(".cache/rag_embeddings")


def _state_hash(parent_docs: Dict[str, Document], chunk_sources: List[str]) -> str:
    h = hashlib.sha256()
    for source in sorted(parent_docs):
        h.update(source.encode())
        h.update(parent_docs[source].content.encode())
    h.update(str(chunk_sources).encode())
    return h.hexdigest()[:20]


class SemanticVectorStore(VectorStore):
    """Dense vector store with chunking and parent-document aggregation.

    Documents are split into ~1000-char chunks before encoding so that no
    content is silently truncated.  similarity_search returns the top-k
    *parent* documents ranked by their highest-scoring chunk — preserving the
    "full skill as one result" behaviour the CLI expects.

    Model: nomic-embed-text-v1.5 (8192-token context, CPU inference to avoid
    competing with other GPU workloads).  Embeddings are cached to disk keyed
    by a SHA-256 content hash so that subsequent runs skip re-encoding.
    """

    MODEL_NAME = "nomic-ai/nomic-embed-text-v1.5"

    def __init__(self) -> None:
        import logging
        logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
        # CPU device: avoids OOM when the GPU is occupied by other processes.
        self._model = SentenceTransformer(
            self.MODEL_NAME,
            trust_remote_code=True,
            local_files_only=False,
            device="cpu",
        )
        # Parent documents, keyed by source.
        self._parent_docs: Dict[str, Document] = {}
        # Chunk tracking (parallel to rows in self._embeddings).
        self._chunk_sources: List[str] = []
        self._embeddings: Optional[np.ndarray] = None

    def add_documents(self, documents: Iterable[Document]) -> None:
        new_docs = list(documents)
        if not new_docs:
            return

        # Pre-compute chunks so the final state hash is known before encoding.
        # This ensures the cache key used to check equals the key used to save.
        pending: List[Tuple[str, str]] = []  # (chunk_text, parent_source)
        for doc in new_docs:
            for chunk in _chunk_text(doc.content):
                pending.append((chunk, doc.source))

        projected_parents = {**self._parent_docs, **{doc.source: doc for doc in new_docs}}
        projected_sources = self._chunk_sources + [src for _, src in pending]
        cache_key = _state_hash(projected_parents, projected_sources)
        cache_npz = _CACHE_DIR / f"{cache_key}.npz"
        cache_pkl = _CACHE_DIR / f"{cache_key}.pkl"

        if cache_npz.exists() and cache_pkl.exists():
            with open(cache_pkl, "rb") as fh:
                state = pickle.load(fh)
            self._parent_docs = state["parent_docs"]
            self._chunk_sources = state["chunk_sources"]
            self._embeddings = np.load(cache_npz)["embeddings"]
            return

        texts = [f"search_document: {chunk}" for chunk, _ in pending]
        new_embeddings = self._model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        for doc in new_docs:
            self._parent_docs[doc.source] = doc
        self._chunk_sources.extend([src for _, src in pending])
        self._embeddings = (
            new_embeddings if self._embeddings is None
            else np.vstack([self._embeddings, new_embeddings])
        )

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.savez(cache_npz, embeddings=self._embeddings)
        with open(cache_pkl, "wb") as fh:
            pickle.dump(
                {"parent_docs": self._parent_docs, "chunk_sources": self._chunk_sources},
                fh,
            )

    def similarity_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        if not self._parent_docs or self._embeddings is None:
            return []
        query_embedding = self._model.encode(
            [f"search_query: {query}"],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        chunk_scores = (self._embeddings @ query_embedding.T).flatten()

        # Aggregate: take the max chunk score per parent document.
        source_scores: Dict[str, float] = {}
        for i, score in enumerate(chunk_scores):
            source = self._chunk_sources[i]
            if score > source_scores.get(source, -1.0):
                source_scores[source] = float(score)

        top_sources = sorted(source_scores, key=lambda s: source_scores[s], reverse=True)[:k]
        return [
            RetrievalResult(document=self._parent_docs[source], score=source_scores[source])
            for source in top_sources
        ]


def _create_store() -> VectorStore:
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
        docs = [
            Document(
                source=str(file_path.relative_to(path)),
                content=file_path.read_text(encoding="utf-8"),
                metadata={"path": str(file_path)},
            )
            for file_path in sorted(path.rglob("*.md"))
        ]
        self.store.add_documents(docs)

    def ingest_skill_namespace(self, directory: str) -> None:
        """Ingest each skill directory (anchored by SKILL.md) as a single document."""
        base = Path(directory)
        if not base.exists() or not base.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        docs = []
        for skill_md in sorted(base.rglob("SKILL.md")):
            skill_dir = skill_md.parent
            content = "\n\n".join(
                f.read_text(encoding="utf-8") for f in sorted(skill_dir.rglob("*.md"))
            )
            source = str(skill_dir.relative_to(base))
            docs.append(Document(
                source=source,
                content=content,
                metadata={"path": str(skill_dir), "type": "skill"},
            ))
        self.store.add_documents(docs)

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
