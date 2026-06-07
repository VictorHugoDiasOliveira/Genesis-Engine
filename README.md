# Genesis Engine

An AI-driven development orchestration platform. Genesis Engine uses RAG (Retrieval-Augmented Generation) so that agents like Claude Code can query relevant knowledge before implementing code, generating tasks, or making decisions. The goal is a system where both business planning and software development are managed and documented by AI agents.

## How It Works

Before writing any code or making any decision, an agent queries the knowledge base to retrieve relevant context — architecture decisions, business rules, prior choices. After acting, it logs what was done to `project_dev_log.md`. This creates a self-documenting, knowledge-grounded development loop.

```
Query RAG → Implement → Log
```

## Project Structure

```
genesis_engine/       Core Python modules (RAG engine, CLI, project journal)
knowledge/
  dev/                Architecture docs, ADRs, technical patterns
  business/           Mission, vision, OKRs, go-to-market
  external/           Skills from skills.sh — best practices, language guides, infra
.agents/skills/       Raw installed skills (tracked in git)
scripts/              Seed and skill-import utilities
docs/                 Vision, architecture, RAG strategy
project_dev_log.md    Single source of truth — every agent action is logged here
```

## Setup

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/<your-org>/Genesis-Engine
cd Genesis-Engine

# Create venv and install dependencies
uv venv .venv
uv pip install sentence-transformers numpy einops --python .venv/bin/python

source .venv/bin/activate
```

## Querying the Knowledge Base

```bash
# Search across all namespaces
python -m genesis_engine.cli query "how to implement chunking for RAG"

# Search a specific namespace
python -m genesis_engine.cli query "go-to-market strategy" --namespace business
python -m genesis_engine.cli query "architecture decisions" --namespace dev
python -m genesis_engine.cli query "Python best practices" --namespace external

# Return more results
python -m genesis_engine.cli query "embedding models" -k 10

# Read the full content of an external skill
python -m genesis_engine.cli read rag/rag-architect
python -m genesis_engine.cli read languages/python/python-best-practices
python -m genesis_engine.cli read best-practices/clean-code

# List all available namespaces
python -m genesis_engine.cli namespaces
```

On the first query, embeddings are computed and cached under `.cache/rag_embeddings/`. Subsequent queries load from cache and are ~5× faster.

## RAG Architecture

The semantic search engine uses `nomic-ai/nomic-embed-text-v1.5` (8192-token context window, CPU inference). Documents are chunked into ~1000-character pieces before encoding; search returns parent documents ranked by their highest-scoring chunk — so you always get a full skill or document as a result, never a fragment.

Knowledge is split into three namespaces:

| Namespace | Content |
|-----------|---------|
| `dev` | Architecture docs, ADRs, technical patterns, code history |
| `business` | Mission/vision, strategy, OKRs, go-to-market |
| `external` | Skills from [skills.sh](https://skills.sh/) — best practices, language guides, infra, testing |

Falls back to TF-IDF if `sentence-transformers` is not installed.

## Adding Skills

Skills from [skills.sh](https://skills.sh/) are installed and automatically added to the RAG knowledge base:

```bash
# Find a relevant skill
npx skills find "react best practices"

# Install it
npx skills add <owner/repo@skill-name>

# Add to the RAG (pick or create a theme)
python scripts/add_skill.py <skill-name> languages/javascript

# The skill is now queryable
python -m genesis_engine.cli query "React component patterns" --namespace external
```

Installed skills live under `.agents/skills/` and are tracked in git. Knowledge copies live under `knowledge/external/<theme>/<skill-name>/`.

## Development Log

Every action taken by an agent is appended to `project_dev_log.md` via `ProjectJournal`:

```python
from genesis_engine.project_journal import ProjectJournal

journal = ProjectJournal()
journal.append_entry(
    title="Added authentication module",
    details="Implemented JWT-based auth following the patterns in the python-best-practices skill.",
    category="Implementation",  # Architecture | Implementation | Decision | Task | Documentation
)
```

This log is the single source of truth for all decisions, task history, and architectural choices.

## Seed Script

To run a full ingest-and-search demo:

```bash
python scripts/seed_rag.py
```

This ingests all three knowledge namespaces and runs a sample query.
