# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Genesis Engine is an AI-driven development orchestration platform. It uses RAG (Retrieval-Augmented Generation) so that agents like Claude Code can query relevant knowledge before implementing code, generating tasks, or making decisions. The goal is a system where business planning and software development are both managed and documented by AI agents.

**Before implementing anything**, query the knowledge base for relevant context (architecture decisions, business rules, prior decisions). After each implementation, append a summary to `project_dev_log.md`.

## Running the Prototype

The project has no external dependencies in its current prototype state — only the Python standard library is used.

```bash
# Run the RAG seed/demo script
python scripts/seed_rag.py
```

To upgrade to real embeddings (optional), install from `requirements.txt` after uncommenting the desired packages.

## Architecture

### Core Modules (`genesis_engine/`)

- **`rag.py`** — The RAG engine. Implements `Document`, `SimpleVectorStore` (TF-IDF cosine similarity, no external deps), `RAGKnowledgeBase` (per-namespace ingestion and search), and `KnowledgeManager` (multi-namespace router). Documents are ingested from markdown directories and searched by string query.

- **`project_journal.py`** — `ProjectJournal` wraps `project_dev_log.md` with structured append (`append_entry`), section-level update (`update_section`), and listing of all entries. This is how agents log decisions and progress.

### Knowledge Namespaces

The RAG is split into two namespaces (as shown in `scripts/seed_rag.py` and `docs/rag-strategy.md`):

| Namespace | Content |
|-----------|---------|
| `dev` | Architecture docs, ADRs, technical patterns, code history |
| `business` | Mission/vision/values, business strategy, OKRs, go-to-market |
| `infra` | Cloud architecture, IaC, Docker, CI/CD, deploy runbooks, monitoring |
| `external` | External sources: Skills.sh, third-party references, industry standards |

Knowledge directory layout: `knowledge/dev/`, `knowledge/business/`, `knowledge/infra/`, `knowledge/external/`.

### Source of Truth

`project_dev_log.md` is the single source of truth for all decisions, task history, and architectural choices. Every agent action that changes the project should be recorded here via `ProjectJournal.append_entry(title, details, category)`.

## Language

All code, comments, documentation, log entries, and any content written by Claude Code must be in English. This applies to every file in the repository.

## Implementation Workflow

Every change in this repository must follow this cycle — no exceptions. This includes code, documentation, configuration files, scripts, and any infrastructure changes (e.g., `.gitignore`, `requirements.txt`):

1. **Query** — search the RAG for relevant context before starting
2. **Implement** — write code or update documentation
3. **Log** — record what was done in `project_dev_log.md` via `ProjectJournal.append_entry()`

**There are no changes too small to log.** Every action taken by Claude Code must be traceable in `project_dev_log.md`.

## Log Entry Categories

All journal entries must use one of these categories:

| Category | When to use |
|----------|-------------|
| `Architecture` | Structural decisions, module design, new abstractions |
| `Implementation` | Code written or changed |
| `Decision` | Any choice between alternatives (library, approach, pattern) |
| `Task` | New tasks defined or completed |
| `Documentation` | Docs created or updated |

## Key Conventions

- **RAG before coding**: Always search the relevant namespace before implementing a feature or making an architectural decision.
- **Log after acting**: Use `ProjectJournal` to record what was done, why, and the category from the table above.
- **Docs as knowledge**: All markdown files in `docs/` are intended to be ingested into the RAG — keep them accurate and up to date, as they directly inform agent behavior.
