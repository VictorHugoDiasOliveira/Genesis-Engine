# RAG Strategy — Genesis Engine

## Purpose

The RAG is the memory of Genesis Engine. Every decision, every skill, every business rule, and every line of architecture lives in the RAG. Agents query it before acting and write to it after acting. Without the RAG, Genesis Engine has no context; with it, the system is permanently informed.

## Hosted Model

The RAG is not a local directory. It is a hosted vector database shared by all projects connected to a Genesis Engine instance. Each project has isolated namespaces so knowledge never bleeds between projects.

**Target backend:** Supabase pgvector (self-hostable, SQL + vector in one place, free tier available) or Pinecone (managed, purpose-built for vectors).

The local prototype uses in-memory stores with disk-cached embeddings (`.cache/rag_embeddings/`). This prototype is the foundation for the hosted implementation.

## Namespace Structure

Each project gets three namespaces:

| Namespace | Content | Who writes |
|-----------|---------|------------|
| `dev` | Architecture docs, ADRs, code patterns, technical decisions, project log | Dev Workflow, Journal |
| `business` | Mission, vision, OKRs, strategy, go-to-market, user research | Business Workflow, Agent Connector |
| `external` | Skills from skills.sh — language guides, best practices, infra patterns | Skills Manager |

## Embedding Model

**Model:** `nomic-ai/nomic-embed-text-v1.5`
- 8192-token context window — handles full skill documents without truncation
- CPU inference — no GPU dependency
- Requires task prefixes: `search_document:` for indexing, `search_query:` for queries

**Chunking:** Documents are split into ~1000-character chunks with 100-character overlap before encoding. Search returns parent documents ranked by their best-scoring chunk (Parent Document Retriever pattern). This means results are always full, coherent documents — never fragments.

## Ingestion Pipelines

### Dev and Business Namespaces
Markdown files are ingested as individual documents. Suitable for focused, single-topic files (ADRs, vision docs, OKR sheets).

### External Namespace (Skills)
Each skill directory (anchored by `SKILL.md`) is ingested as a single parent document with all its reference files concatenated. This preserves skill coherence and ensures a query for "React best practices" returns the entire React skill, not scattered fragments.

### Journal Re-ingestion
After each agent session, the project log entries are re-ingested into the `dev` namespace. This is how the system learns from its own history.

## Query Rules

1. **Always query before acting.** No code is written, no task is created, and no architectural decision is made without a prior RAG query.
2. **Namespace routing.** Business decisions query `business`; technical decisions query `dev`; implementation details query `external`.
3. **Multi-namespace for cross-cutting concerns.** A task that spans business and tech (e.g. "define the data model for user game lists") queries both `business` and `dev`.

## Cache Strategy

Embeddings are cached to disk keyed by a SHA-256 hash of the document content. The cache is automatically invalidated when any document in the namespace changes. This reduces repeat query overhead from ~100s to ~21s on a cold model load.

In the hosted implementation, the vector database persists embeddings permanently — no re-encoding on each API call.

## Evolution

As projects grow, the RAG grows with them. Every ADR, every task completion, every business pivot is ingested. The system's retrieval quality improves over time as the knowledge base becomes more complete and precise.
