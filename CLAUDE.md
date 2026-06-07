# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Genesis Engine is an AI-driven development orchestration platform. It uses RAG (Retrieval-Augmented Generation) so that agents like Claude Code can query relevant knowledge before implementing code, generating tasks, or making decisions. The goal is a system where business planning and software development are both managed and documented by AI agents.

**Before implementing anything**, query the knowledge base for relevant context (architecture decisions, business rules, prior decisions). After each implementation, append a summary to `project_dev_log.md`.

## Setup

Semantic search requires `sentence-transformers` and `numpy`. A virtual environment is included:

```bash
# Create and populate the venv (first time only)
uv venv .venv
uv pip install sentence-transformers numpy einops --python .venv/bin/python

# Always use the venv python to run CLI commands
source .venv/bin/activate
```

## Running the CLI

```bash
# Query the knowledge base (all namespaces)
python -m genesis_engine.cli query "your question"

# Query a specific namespace
python -m genesis_engine.cli query "your question" --namespace external

# Increase number of results
python -m genesis_engine.cli query "your question" -k 10

# Read full content of an external skill theme
python -m genesis_engine.cli read best-practices/clean-code
python -m genesis_engine.cli read languages/python/building-python-clis

# List available namespaces
python -m genesis_engine.cli namespaces
```

To upgrade to real embeddings (optional), install from `requirements.txt` after uncommenting the desired packages.

## Architecture

### Core Modules (`genesis_engine/`)

- **`rag.py`** — The RAG engine. `SimpleVectorStore` (TF-IDF fallback, no deps). `SemanticVectorStore` uses `nomic-embed-text-v1.5` (8192-token context, CPU, disk-cached embeddings under `.cache/rag_embeddings/`). Documents are chunked into ~1000-char pieces before encoding; `similarity_search` returns parent documents ranked by max chunk score (Parent Document Retriever pattern). nomic requires `search_document:` and `search_query:` prefixes. `RAGKnowledgeBase` handles per-namespace ingestion. `KnowledgeManager` routes across namespaces.

- **`project_journal.py`** — `ProjectJournal` wraps `project_dev_log.md` with structured append (`append_entry`), section-level update (`update_section`), and listing of all entries. This is how agents log decisions and progress.

### Knowledge Namespaces

The RAG is split into two namespaces (as shown in `scripts/seed_rag.py` and `docs/rag-strategy.md`):

| Namespace | Content |
|-----------|---------|
| `dev` | Architecture docs, ADRs, technical patterns, code history |
| `business` | Mission/vision/values, business strategy, OKRs, go-to-market |
| `external` | Skills.sh exports, third-party references, best practices — organized by theme in subdirectories (e.g. `infra/`, `database/`, `clean-code/`) |

Knowledge directory layout: `knowledge/dev/`, `knowledge/business/`, `knowledge/external/`.

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

## Skill Workflow (Skills.sh)

Skills from [skills.sh](https://skills.sh/) extend agent capabilities and feed the RAG with external knowledge. Use this workflow autonomously whenever a task would benefit from external best practices:

1. **Identify the need** — based on the current task, determine what external knowledge would help (e.g. building a CLI → look for `clean-code` or `python-best-practices`)
2. **Find the skill** — use `npx skills find <query>` or browse skills.sh. Prefer skills with 1K+ installs from reputable sources
3. **Install** — `npx skills add <owner/repo@skill-name>` installs to `.agents/skills/<skill-name>/`
4. **Add to RAG** — run `python scripts/add_skill.py <skill-name> <theme>` to copy the skill into `knowledge/external/<theme>/`
5. **Log** — record the skill added and why in `project_dev_log.md`

```bash
# Example: adding a clean-code skill before building the CLI
npx skills add <owner/repo@clean-code>
python scripts/add_skill.py clean-code clean-code
```

Skill themes map to `knowledge/external/` subdirectories. Default themes to reuse when applicable:

| Theme | Content |
|-------|---------|
| `best-practices/` | Language-agnostic clean code, general patterns |
| `languages/<lang>/` | Language-specific skills (e.g. `languages/python/`, `languages/javascript/`) |
| `infra/` | Docker, CI/CD, cloud, IaC |
| `database/` | SQL, NoSQL, data modeling |
| `testing/` | Testing strategies, any language |
| `agent-skills/` | Skills about agent workflows and capabilities |

If a skill does not fit any existing theme, create a new descriptive subdirectory. Themes are a convention, not a closed list.

## Key Conventions

- **RAG before coding**: Always search the relevant namespace before implementing a feature or making an architectural decision.
- **Skills before complex tasks**: If a task involves a domain with likely external best practices, proactively find and install a relevant skill before starting.
- **Log after acting**: Use `ProjectJournal` to record what was done, why, and the category from the table above.
- **Docs as knowledge**: All markdown files in `docs/` are intended to be ingested into the RAG — keep them accurate and up to date, as they directly inform agent behavior.
- **README always current**: Update `README.md` whenever a change affects the CLI, RAG architecture, knowledge structure, setup steps, or core workflows. The README serves as context for both humans and agents — a stale README is a knowledge gap.
