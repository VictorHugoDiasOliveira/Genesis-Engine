# Genesis-Engine

Genesis-Engine is an AI-driven development orchestration engine.

## Project Structure

- `docs/` — vision, architecture, roadmap, and RAG strategy documentation
- `genesis_engine/` — Python implementation of the RAG prototype and project journal
- `project_dev_log.md` — central history and decision log for the project
- `scripts/seed_rag.py` — example of document ingestion and semantic search
- `requirements.txt` — optional dependencies for evolving the engine

## Goals

- Build separate RAGs for development and business planning
- Ensure Claude Code always queries the RAG before implementing
- Automatically update the development log after each step

## Getting Started

1. Read the documents in `docs/`.
2. Use `scripts/seed_rag.py` to test markdown ingestion.
3. Update `project_dev_log.md` with decisions, missions, and values.
