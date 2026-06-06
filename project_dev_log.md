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

## Add skill ingestion workflow and add_skill.py script — Implementation

- **Date:** 2026-06-06T23:00:16Z
- **Category:** Implementation

Created scripts/add_skill.py to bridge Skills.sh and the RAG knowledge base.
The script reads skill content from .agents/skills/<skill-name>/ and copies markdown files to knowledge/external/<theme>/.
This enables autonomous skill discovery: identify need → find skill → install → add to RAG → log.
Added find-skills skill to knowledge/external/agent-skills/ as first example.
Updated CLAUDE.md with the full skill workflow including when to proactively look for skills.

## Define knowledge/external/ theme conventions — Decision

- **Date:** 2026-06-06T23:03:00Z
- **Category:** Decision

Defined default themes for knowledge/external/ subdirectories: best-practices, languages/<lang>, infra, database, testing, agent-skills.
Themes are a convention, not a closed list — new themes can be created whenever a skill does not fit an existing one.
Updated CLAUDE.md with the theme table and the explicit note that themes are extensible.

## Install and ingest 7 Python skills for CLI development — Task

- **Date:** 2026-06-06T23:08:58Z
- **Category:** Task

Installed and ingested the following skills from Skills.sh in preparation for item 2 (interactive CLI):

best-practices/clean-code (245 installs) — naming, functions, classes, error handling, tests
languages/python/building-python-clis (76 installs) — Python CLI best practices
languages/python/python-performance-optimization (25.4K installs) — advanced patterns, profiling
languages/python/python-mcp-server-generator (9.6K installs) — MCP server generation patterns
languages/python/dataverse-python-advanced-patterns (8.9K installs) — advanced Python patterns
testing/temporal-python-testing (7.2K installs) — unit, integration, replay testing
languages/python/python-best-practices (1.6K installs) — general Python best practices

Fixed add_skill.py to place each skill in its own subdirectory (knowledge/external/<theme>/<skill-name>/) to prevent file collisions when multiple skills share a theme.

## RAG: index external skills by theme instead of by file — Architecture

- **Date:** 2026-06-06T23:13:59Z
- **Category:** Architecture

Added ingest_skill_namespace() to RAGKnowledgeBase and KnowledgeManager.
Each skill directory (anchored by SKILL.md) is ingested as a single document by concatenating all its markdown files.
This means the RAG returns themes like 'best-practices/clean-code' instead of individual files like 'chapters/functions.md'.
The agent now reads the full skill content after receiving a relevant theme from the RAG.
Updated seed_rag.py to use ingest_skill_namespace() for the external namespace.
SKILL.md presence is used as the anchor to identify skill root directories — ties directly to the add_skill.py convention.

## Implement interactive CLI (item 2) — Implementation

- **Date:** 2026-06-06T23:15:44Z
- **Category:** Implementation

Created genesis_engine/cli.py with three subcommands:
- query <text> — searches the knowledge base across all or selected namespaces, returns themes with scores
- read <theme> — prints full content of an external skill theme (e.g. best-practices/clean-code)
- namespaces — lists all available namespaces

Built with argparse (zero external deps). Follows clean-code and python-best-practices skills:
small focused functions, one responsibility per command, descriptive names, clear output.
Namespace loading is automatic: dev and business use ingest_markdown_directory, external uses ingest_skill_namespace.
Updated CLAUDE.md with full CLI usage examples.

## CLI: add minimum score threshold to filter noise — Implementation

- **Date:** 2026-06-06T23:20:18Z
- **Category:** Implementation

Added --min-score option to the query command (default: 0.10).
Results below the threshold were showing irrelevant documents due to coincidental token overlap in TF-IDF similarity.
Default of 0.10 filters out noise while keeping genuinely relevant results.
User can override with --min-score 0.05 for broader results or --min-score 0.20 for stricter filtering.

