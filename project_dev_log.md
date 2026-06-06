# Genesis Engine - Development Log

## Mission
Build an AI engine that manages business planning and technical development.

## Vision
Enable any project to grow with automated agent support.

## Values
- Transparency
- Continuous evolution
- Alignment between business and engineering
- Documentation as the source of truth

## Strategy
- Centralize knowledge in RAGs.
- Use AI to translate objectives into tasks and code.
- Always update the history of decisions and implementations.

---

## Log

<!-- All entries below are appended by agents using ProjectJournal.append_entry().
     Valid categories: Architecture | Implementation | Decision | Task | Documentation -->
## Project Foundation Setup — Documentation

- **Date:** 2026-06-06T22:42:54Z
- **Category:** Documentation

Translated all files from Portuguese to English (code, docs, strings, comments).
Added CLAUDE.md with architecture overview, implementation workflow, and log entry categories.
Formalized the Query → Implement → Log cycle as a mandatory rule for all agent actions.
Cleaned up docs/genesis-vision.md (removed duplicated sections, consolidated content).
Restructured project_dev_log.md with defined log entry categories.

## Add .gitignore and remove tracked __pycache__ — Implementation

- **Date:** 2026-06-06T22:42:54Z
- **Category:** Implementation

Created .gitignore to exclude Python bytecode (__pycache__, *.pyc), virtual environments,
build artifacts, IDE files, and future vector store files (*.faiss, *.index, chroma/).
Removed already-tracked genesis_engine/__pycache__/ files from git history.

## Create knowledge/ directory structure — Implementation

- **Date:** 2026-06-06T22:45:05Z
- **Category:** Implementation

Created knowledge/ with three namespaces: dev, business, external.
- knowledge/dev/: architecture.md, rag-strategy.md, roadmap.md — technical knowledge
- knowledge/business/: genesis-vision.md — mission, vision, strategy
- knowledge/external/: reserved for external sources (Skills.sh, third-party refs)
Each namespace has a README.md describing its purpose and what to add.
Updated scripts/seed_rag.py to ingest from knowledge/ namespaces instead of docs/.
Verified ingestion works: all three namespaces return results for semantic queries.

## Add infra namespace to knowledge base — Decision

- **Date:** 2026-06-06T22:48:50Z
- **Category:** Decision

Added knowledge/infra/ as a dedicated RAG namespace for infrastructure knowledge.
Rationale: infra context (cloud, IaC, CI/CD, deploy) is distinct from dev and should not pollute code/architecture queries.
Updated scripts/seed_rag.py to ingest knowledge/infra/ into the infra namespace.
Updated CLAUDE.md knowledge namespace table to include infra and external with descriptions.
All four namespaces (dev, business, infra, external) verified working.

## Reorganize knowledge/ — remove infra namespace — Decision

- **Date:** 2026-06-06T22:53:29Z
- **Category:** Decision

Removed knowledge/infra/ as a top-level namespace.
Rationale: external/ already covers infra content from Skills.sh and third-party references.
Having a separate infra namespace created redundancy when all external knowledge (infra, database, clean-code, etc.) comes from the same origin.
external/ now uses subdirectories to organize by theme (e.g. infra/, database/, clean-code/).
Updated seed_rag.py, CLAUDE.md namespace table, and external/README.md accordingly.

