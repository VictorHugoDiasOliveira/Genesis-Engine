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

## Install rag-architect and rag-implementation skills — Task

- **Date:** 2026-06-06T23:22:27Z
- **Category:** Task

Installed two RAG-specific skills and added to knowledge/external/rag/:
- jeffallan/claude-skills@rag-architect (2.7K installs) — chunking strategies, embedding models, vector databases, retrieval optimization, RAG evaluation
- wshobson/agents@rag-implementation (from wshobson/agents) — RAG implementation patterns and details
Both verified in RAG: appear at top results for 'RAG semantic search vector database' queries.

## Replace TF-IDF with semantic embeddings (sentence-transformers) — Architecture

- **Date:** 2026-06-06T23:41:11Z
- **Category:** Architecture

Replaced SimpleVectorStore (TF-IDF cosine) with SemanticVectorStore using sentence-transformers.
Model: all-MiniLM-L6-v2 (384 dimensions, fast, free, local — as recommended by embedding-strategies and rag-architect skills).
SimpleVectorStore kept as automatic fallback when sentence-transformers is not installed.
Store selection is automatic via _create_store() based on import availability.
Results are now semantically ranked: 'How to build a rag?' correctly returns rag/rag-architect (0.38) and rag/rag-implementation (0.31) at the top.
Added uv venv .venv setup instructions to CLAUDE.md.
Dependencies: sentence-transformers and numpy added to requirements.txt and installed in .venv.

## RAG Implementation Review — Three Fixes Applied — Implementation

- **Date:** 2026-06-07T00:45:28Z
- **Category:** Implementation

Reviewed the full RAG implementation after gaining context from rag-architect, rag-implementation, and embedding-strategies skills. Found and fixed three issues.

1. Critical: Silent token truncation (fixed). all-MiniLM-L6-v2 had a 256-token limit. Skill documents (multiple concatenated .md files) easily exceeded 50,000 characters. Only the first ~200 words of each skill were being embedded; the rest was silently discarded. Switched to nomic-ai/nomic-embed-text-v1.5 (8192-token context, ~270MB). Uses device=cpu to avoid competing with other GPU workloads. Also implemented chunking (1000-char chunks, 100-char overlap) using the Parent Document Retriever pattern: documents are split before encoding, but similarity_search returns parent documents ranked by their best chunk score. The nomic model requires task prefixes: search_document: for indexing and search_query: for queries.

2. Important: Re-embedding on every run (fixed). Embeddings were recomputed from scratch every time the CLI ran. SemanticVectorStore now writes embeddings and chunk metadata to .cache/rag_embeddings/ after first ingestion. Subsequent runs load from disk and skip encoding. Cache key is a SHA-256 of the projected final state computed before encoding so the check key always equals the save key. Result: 1:40 first run down to 21s subsequent runs.

3. Minor: Non-batched ingestion (fixed). ingest_markdown_dir and ingest_skill_namespace previously called add_documents one document at a time. Now they collect all documents first and call add_documents once per namespace.

Files changed: genesis_engine/rag.py, requirements.txt (added einops), CLAUDE.md (updated setup command and architecture note).

## README.md Updated — Full Project Documentation — Documentation

- **Date:** 2026-06-07T00:48:11Z
- **Category:** Documentation

Rewrote README.md to reflect the current state of the project. Added sections covering: how the RAG loop works (Query -> Implement -> Log), project structure, setup instructions with uv, full CLI usage with examples (query, read, namespaces), RAG architecture explanation (nomic model, chunking, parent-document retrieval), skills workflow (find, install, add_skill.py), and ProjectJournal usage. Replaced the minimal 3-section stub with production-ready documentation.

## Rule Added — README.md Must Always Be Kept Up to Date — Decision

- **Date:** 2026-06-07T00:49:32Z
- **Category:** Decision

Added explicit rule to CLAUDE.md: README.md must be updated whenever a change affects the CLI, RAG architecture, knowledge structure, setup steps, or core workflows. The README serves as context for both humans and agents. Also saved as a feedback memory so the rule persists across conversations.

## Vision Clarified — Genesis Engine as Centralized Autonomous Platform — Documentation

- **Date:** 2026-06-07T01:09:39Z
- **Category:** Documentation

Rewrote all core documentation to reflect the true vision of Genesis Engine: a centralized hosted platform that consuming projects connect to, not a local library they embed.

Key changes across all docs:
- genesis-vision.md: describes the platform model (projects connect to Genesis Engine, not embed it), multi-LLM by design, the knowledge loop, and full lifecycle responsibility
- architecture.md: shows the centralized architecture diagram, all core components (Hosted RAG, Agent Connector, Skills Manager, Orchestration Layer, Project Registry), data flow, and current implementation state table
- rag-strategy.md: updated for hosted model (Supabase pgvector), per-project namespaces, journal re-ingestion, and the prototype-to-hosted migration path
- roadmap.md: four phases — (1) Hosted RAG, (2) Agent Connector + Business Workflow, (3) Autonomous Skills Manager + Task Engine, (4) Infra/Deploy — with clear exit criteria per phase
- README.md: updated to reflect current state table, new vision, and links to all docs

All docs/ files synced to knowledge/ for RAG ingestion. Cache invalidated. Vision also saved to persistent memory.

## Structural Refactor — Abstract Interfaces and Config Foundation — Architecture

- **Date:** 2026-06-07T01:19:16Z
- **Category:** Architecture

Aligned codebase with the Genesis Engine platform vision (hosted, multi-project).

Changes:
- rag.py: Added VectorStore ABC (abstractmethod add_documents and similarity_search). SimpleVectorStore and SemanticVectorStore now implement VectorStore. _create_store() return type is VectorStore. Phase 1 will add HostedVectorStore without touching existing implementations.
- project_journal.py: Added Journal ABC (abstractmethod append_entry, read_log, list_entries). ProjectJournal implements Journal. Phase 1 will add HostedJournal.
- config.py (new): GenesisConfig dataclass loaded from genesis.yaml via pyyaml. Supports mode=local (default) and mode=hosted (Phase 1). Provides knowledge_dir, llm_routing (per-task LLM provider), and API connection settings. Falls back to all defaults when no genesis.yaml exists.
- cli.py: Now loads GenesisConfig via load_config() instead of hardcoding ROOT/knowledge. Raises NotImplementedError with a clear message when mode=hosted is set before Phase 1 is built.
- requirements.txt: Added pyyaml.
- CLAUDE.md: Added This Repository section clarifying this is the engine repo, not a consuming project. Updated Architecture section to mention VectorStore ABC, config.py, and Journal ABC.
- README.md: Updated setup command with pyyaml.

## CLI Fix — Resolves genesis.yaml from CWD for Consuming Projects — Implementation

- **Date:** 2026-06-07T01:29:00Z
- **Category:** Implementation

Fixed a design bug where the CLI always resolved genesis.yaml and knowledge_dir relative to the Genesis Engine repo root (ROOT), making it impossible for consuming projects (e.g. MyGameList) to use their own config.

New behavior: _resolve_config() checks CWD/genesis.yaml first (consuming project), then falls back to ROOT/genesis.yaml (engine development). knowledge_dir is resolved relative to the config file's parent directory, not the engine root.

Also removed the now-unused _knowledge_external() helper.

Validated: running `python -m genesis_engine.cli namespaces` from MyGameList/ correctly loads MyGameList's knowledge/ namespaces.

## Phase 2 — Agent Connector and Business Workflow Implemented — Implementation

- **Date:** 2026-06-07T02:31:58Z
- **Category:** Implementation

Implemented the Agent Connector and Business Workflow (Phase 2 of the Genesis Engine roadmap).

genesis_engine/agent.py (new):
- AgentConnector class with unified chat() and stream() methods
- Supports DeepSeek, OpenAI (GPT), and Gemini via OpenAI-compatible SDK
- Provider routing via GenesisConfig.llm_routing (per task type)
- API keys read exclusively from environment variables (DEEPSEEK_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY)

genesis_engine/business_workflow.py (new):
- run(idea, config, base_dir) generates a 5-section business plan
- Sections: vision, market, product, business-model, okrs
- Each section saved as markdown to knowledge/business/
- Logs session to project_dev_log.md via ProjectJournal

genesis_engine/cli.py:
- Added `plan` subcommand: python -m genesis_engine.cli plan "<idea>"

requirements.txt:
- Added openai package

Validated: agent and workflow instantiate correctly. API call blocked by insufficient DeepSeek balance — awaiting top-up to run end-to-end test.

## Add genesis ask — RAG-backed Q&A command — Implementation

- **Date:** 2026-06-07T16:25:50Z
- **Category:** Implementation

Added `genesis ask` command that allows natural language questions answered by the LLM using knowledge base context retrieved via RAG.

New file: genesis_engine/ask_workflow.py
- Queries KnowledgeManager for relevant docs (threshold >= 0.10)
- Sorts by score, caps context at 12,000 chars
- Streams LLM response to stdout
- Routes to `analysis` task in llm_routing config

Updated: genesis_engine/cli.py — added `ask` subcommand with --namespace and -k flags
Updated: README.md — documented the ask command

Usage: genesis ask "what is the target audience?"

## Add genesis.yaml to Genesis Engine root — Implementation

- **Date:** 2026-06-07T17:16:35Z
- **Category:** Implementation

Added genesis.yaml to the engine's own repository so that `genesis ask`, `genesis query`, and `genesis plan` work when run from the Genesis Engine directory itself.

Config: mode=local, knowledge_dir=knowledge, all LLM tasks routed to groq.

## Add genesis stack command — tech stack advisor — Implementation

- **Date:** 2026-06-07T18:31:44Z
- **Category:** Implementation

New workflow: genesis_engine/stack_workflow.py
New CLI command: genesis stack [preferences]

Reads the business RAG (product, market, vision docs) as context, incorporates optional user-specified technology preferences, and asks the LLM to produce a comprehensive stack decision document.

Output saved to knowledge/dev/stack.md in the consuming project.
Logs the decision to project_dev_log.md.

This command fills the gap between business planning (genesis plan) and development — ensuring tech decisions are always grounded in business context.

