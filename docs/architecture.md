# Genesis Engine — Architecture

## Overview

Genesis Engine is a centralized platform. Projects connect to it via API; they do not embed it. The platform owns the knowledge, the agents, the skills, and the workflows. Consuming projects own only their domain code.

```
┌──────────────────────────────────────────────────────────┐
│                     Genesis Engine                        │
│                                                          │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │  Hosted RAG │   │    Agent     │   │   Skills     │  │
│  │  (per-proj  │◄──│  Connector   │   │   Manager    │  │
│  │  namespace) │   │  multi-LLM   │   │  (auto-ingest│  │
│  └──────┬──────┘   └──────┬───────┘   └──────┬───────┘  │
│         │                 │                  │           │
│  ┌──────▼──────────────────▼──────────────────▼───────┐  │
│  │              Orchestration Layer                    │  │
│  │   Business Workflow · Task Engine · Dev Workflow   │  │
│  │   Infra Agent · Deploy Agent · Journal             │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────┘
                            │ API
           ┌────────────────┼────────────────┐
           │                │                │
      MyGameList       Project B         Project C
      (domain code)   (domain code)    (domain code)
```

## Core Components

### 1. Hosted RAG Service

The knowledge base is not a local directory — it is a hosted vector database (Supabase pgvector or equivalent) accessible to all connected projects via API.

Each project gets its own namespaces:

| Namespace | Content |
|-----------|---------|
| `dev` | Architecture docs, ADRs, code patterns, technical decisions |
| `business` | Mission, vision, OKRs, strategy, go-to-market |
| `external` | Skills from skills.sh — best practices, language guides, infra patterns |

Embeddings use `nomic-ai/nomic-embed-text-v1.5` (8192-token context). Documents are chunked before encoding and search returns parent documents ranked by best-chunk score.

### 2. Agent Connector

A unified client that routes tasks to the appropriate LLM provider. The user configures which provider to use per task type or sets a default.

Supported providers: **GPT (OpenAI)**, **Gemini (Google)**, **DeepSeek**, and any OpenAI-compatible API.

Every agent call is enriched with RAG context before being sent to the model. Responses are parsed and stored back into the relevant namespace.

### 3. Skills Manager

Autonomous skill management — Genesis Engine decides what skills a project needs, finds them on skills.sh, installs them, and ingests them into the `external` namespace.

No human intervention required. When a project starts a new domain (e.g. adding a React frontend), Genesis Engine fetches the relevant skill and the RAG is ready before the first line of code is written.

### 4. Orchestration Layer

High-level workflows that combine the components above:

- **Business Workflow** — takes a project idea, runs an AI-driven planning session, saves strategy and OKRs to the `business` namespace
- **Task Engine** — generates, prioritizes, and tracks tasks from RAG context and business objectives
- **Dev Workflow** — queries RAG before every implementation; writes code, ADRs, and documentation
- **Infra Agent** — provisions infrastructure based on architecture decisions in the RAG
- **Deploy Agent** — handles CI/CD pipelines and production deployments
- **Journal** — every action by every agent is appended to the project log; the log is re-ingested into the RAG after each session

### 5. Project Registry

A lightweight configuration that connects a project to Genesis Engine:

```yaml
# genesis.yaml (in the consuming project)
project: my-game-list
genesis_engine_url: https://api.genesis-engine.io   # or self-hosted
api_key: <key>
default_llm: deepseek                               # or gpt-4, gemini, etc.
llm_routing:
  business: gpt-4
  code: deepseek
  analysis: gemini
```

That is the only Genesis Engine artifact inside a consuming project.

## Data Flow

```
User describes idea
      │
      ▼
Agent Connector (LLM of choice)
      │  enriched with RAG context
      ▼
Business Workflow → saves to business namespace
      │
      ▼
Skills Manager → fetches relevant skills → saves to external namespace
      │
      ▼
Task Engine → generates tasks from RAG
      │
      ▼
Dev Workflow → queries RAG → generates code
      │
      ▼
Journal → logs everything → re-ingested into RAG
      │
      ▼
Infra/Deploy Agent → provisions and deploys
```

## Current Implementation State

The current codebase is a working prototype of the local components:

| Component | Status |
|-----------|--------|
| Local RAG (nomic embeddings + chunking + disk cache) | ✅ Done |
| CLI for querying the knowledge base | ✅ Done |
| ProjectJournal (append-only log) | ✅ Done |
| Skills ingestion from skills.sh | ✅ Done |
| Hosted RAG Service | 🔲 Phase 1 |
| Agent Connector (multi-LLM) | 🔲 Phase 2 |
| Business Workflow | 🔲 Phase 2 |
| Skills Manager (autonomous) | 🔲 Phase 3 |
| Task Engine | 🔲 Phase 3 |
| Infra/Deploy Agent | 🔲 Phase 4 |
