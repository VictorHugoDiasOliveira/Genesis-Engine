from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


@dataclass
class Document:
    source: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    document: Document
    score: float


def normalize_text(text: str) -> List[str]:
    words = re.findall(r"\w+", text.lower())
    return [word for word in words if len(word) > 1]


def cosine_similarity(a: Counter, b: Counter) -> float:
    intersection = set(a.keys()) & set(b.keys())
    numerator = sum(a[token] * b[token] for token in intersection)
    sum_a = sum(value * value for value in a.values())
    sum_b = sum(value * value for value in b.values())
    denominator = math.sqrt(sum_a) * math.sqrt(sum_b)
    return numerator / denominator if denominator else 0.0


class SimpleVectorStore:
    def __init__(self) -> None:
        self.documents: List[Document] = []
        self.vectors: List[Counter] = []

    def add_documents(self, documents: Iterable[Document]) -> None:
        for document in documents:
            tokens = normalize_text(document.content)
            vector = Counter(tokens)
            self.documents.append(document)
            self.vectors.append(vector)

    def similarity_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        query_vector = Counter(normalize_text(query))
        scores: List[Tuple[int, float]] = []
        for index, vector in enumerate(self.vectors):
            score = cosine_similarity(query_vector, vector)
            scores.append((index, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        results: List[RetrievalResult] = []
        for index, score in scores[:k]:
            results.append(RetrievalResult(document=self.documents[index], score=score))
        return results


class RAGKnowledgeBase:
    def __init__(self, name: str) -> None:
        self.name = name
        self.store = SimpleVectorStore()

    def ingest_document(self, source: str, content: str, metadata: Optional[Dict[str, str]] = None) -> None:
        metadata = metadata or {}
        document = Document(source=source, content=content, metadata=metadata)
        self.store.add_documents([document])

    def ingest_markdown_dir(self, directory: str) -> None:
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")

        for file_path in sorted(path.rglob("*.md")):
            source = str(file_path.relative_to(path))
            content = file_path.read_text(encoding="utf-8")
            metadata = {"path": str(file_path)}
            self.ingest_document(source=source, content=content, metadata=metadata)

    def search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        return self.store.similarity_search(query, k=k)


class KnowledgeManager:
    def __init__(self) -> None:
        self.namespaces: Dict[str, RAGKnowledgeBase] = {}

    def add_namespace(self, name: str) -> RAGKnowledgeBase:
        if name in self.namespaces:
            return self.namespaces[name]
        kb = RAGKnowledgeBase(name=name)
        self.namespaces[name] = kb
        return kb

    def search(self, query: str, k: int = 5, namespaces: Optional[List[str]] = None) -> Dict[str, List[RetrievalResult]]:
        selected = namespaces if namespaces is not None else list(self.namespaces.keys())
        results: Dict[str, List[RetrievalResult]] = {}
        for namespace in selected:
            kb = self.namespaces.get(namespace)
            if kb is None:
                continue
            results[namespace] = kb.search(query, k=k)
        return results

    def ingest_markdown_directory(self, namespace: str, directory: str) -> None:
        kb = self.add_namespace(namespace)
        kb.ingest_markdown_dir(directory)

    def list_namespaces(self) -> List[str]:
        return sorted(self.namespaces.keys())
