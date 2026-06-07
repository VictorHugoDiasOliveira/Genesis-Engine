# Genesis Engine

An autonomous AI-driven development orchestration platform. Genesis Engine acts as the brain behind any software project — from the first business idea to production deployment.

**Projects do not contain Genesis Engine. They connect to it.**

## What It Does

You describe an idea. Genesis Engine handles the rest:

1. **Business planning** — opens an AI-driven session (your choice of GPT, Gemini, DeepSeek, or others) to develop mission, vision, OKRs, and strategy
2. **Knowledge management** — saves all decisions to a hosted RAG, per project, per namespace
3. **Skills** — autonomously discovers and ingests relevant best-practice skills before writing code
4. **Development** — generates tasks, architecture decisions, and code — always consulting the RAG
5. **Infrastructure & deploy** — provisions infra and manages deployment pipelines

The consuming project contains only its domain code. No local knowledge bases, no skill directories, no manual RAG configuration — just a `genesis.yaml` pointing to the engine.

## Current State

The local prototype is complete and functional. It validates the core loop:

```
Query RAG → Implement → Log → RAG (smarter next time)
```

| Component | Status |
|-----------|--------|
| Semantic RAG (nomic-embed-text-v1.5, chunking, disk cache) | ✅ |
| CLI for querying the knowledge base | ✅ |
| Skills ingestion from skills.sh | ✅ |
| ProjectJournal (append-only decision log) | ✅ |
| Hosted RAG Service (Supabase pgvector) | 🔲 Phase 1 |
| Agent Connector (GPT / Gemini / DeepSeek) | 🔲 Phase 2 |
| Business Workflow (`genesis plan`) | 🔲 Phase 2 |
| Autonomous Skills Manager | 🔲 Phase 3 |
| Task Engine | 🔲 Phase 3 |
| Infra & Deploy Agent | 🔲 Phase 4 |

See [docs/roadmap.md](docs/roadmap.md) for the full phase breakdown.

## Setup (Prototype)

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/VictorHugoDiasOliveira/Genesis-Engine
cd Genesis-Engine

uv venv .venv
uv pip install sentence-transformers numpy einops pyyaml --python .venv/bin/python
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

# List available namespaces
python -m genesis_engine.cli namespaces
```

On the first query, embeddings are computed and cached under `.cache/rag_embeddings/`. Subsequent queries skip re-encoding (~21s vs ~100s).

## Adding Skills

```bash
# Find a skill
npx skills find "react best practices"

# Install it
npx skills add <owner/repo@skill-name>

# Add to the RAG
python scripts/add_skill.py <skill-name> languages/javascript

# Now queryable
python -m genesis_engine.cli query "React component patterns" --namespace external
```

## Project Structure

```
genesis_engine/       Core engine — RAG, CLI, journal
knowledge/
  dev/                Architecture docs, ADRs, roadmap, RAG strategy
  business/           Vision, strategy, OKRs
  external/           Skills from skills.sh
.agents/skills/       Raw installed skills (tracked in git)
docs/                 Source documents (synced to knowledge/)
scripts/              Seed and skill-import utilities
project_dev_log.md    Append-only decision log — single source of truth
```

## Documentation

- [Vision](docs/genesis-vision.md) — what Genesis Engine is and why
- [Architecture](docs/architecture.md) — components, data flow, current state
- [RAG Strategy](docs/rag-strategy.md) — embedding model, namespaces, ingestion rules
- [Roadmap](docs/roadmap.md) — phases from prototype to full platform
