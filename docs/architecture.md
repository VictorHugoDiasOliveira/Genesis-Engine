# Genesis Engine — Architecture

## Overview

Genesis Engine is a centralized platform. Projects connect to it via API; they do not embed it. The platform owns the knowledge, the agents, the skills, and the workflows. Consuming projects own only their domain code.

```
┌──────────────────────────────────────────────────────────┐
│                     Genesis Engine                       │
│                                                          │
│  ┌─────────────┐   ┌──────────────┐    ┌──────────────┐  │
│  │  Hosted RAG │   │    Agent     │    │   Skills     │  │
│  │  (per-proj  │◄──│  Connector   │    │   Manager    │  │
│  │  namespace) │   │  multi-LLM   │    │ (auto-ingest)│  │
│  └──────┬──────┘   └──────┬───────┘    └──────┬───────┘  │
│         │                 │                   │          │
│  ┌──────▼──────────────────▼──────────────────▼───────┐  │
│  │              Orchestration Layer                   │  │
│  │  Business · Stack · Ask · Task · Dev · Infra/Deploy│  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────┬──────────────────────────────┘
                            │ API
                            │
                        MyGameList
                       (domain code)
```

## Core Components

### 1. Hosted RAG Service

The knowledge base is not a local directory — it is a hosted vector database (Supabase pgvector or equivalent) accessible to all connected projects via API.

Each project gets its own namespaces:

| Namespace | Content |
|-----------|---------|
| `dev` | Architecture docs, ADRs, code patterns, stack decisions, technical decisions |
| `business` | Mission, vision, OKRs, strategy, go-to-market |
| `external` | Skills from skills.sh — best practices, language guides, infra patterns |

Embeddings use `nomic-ai/nomic-embed-text-v1.5` (8192-token context). Documents are chunked before encoding and search returns parent documents ranked by best-chunk score (Parent Document Retriever pattern). Embeddings are disk-cached under `.cache/rag_embeddings/` keyed by SHA-256 of the document state.

### 2. Agent Connector

A unified client that routes tasks to the appropriate LLM provider based on `llm_routing` in `genesis.yaml`.

Supported providers: **OpenAI (GPT)**, **Gemini (Google)**, **DeepSeek**, **Groq** (free tier, Llama 3.3), and any OpenAI-compatible API. API keys are read exclusively from environment variables.

Every agent call is enriched with RAG context before being sent to the model.

### 3. Skills Manager

Autonomous skill management — Genesis Engine decides what skills a project needs based on the tech stack document, finds them on skills.sh, installs them, and ingests them into the `external` namespace. No human intervention required.

Skills are installed to `.agents/skills/<name>/` and tracked in `skills-lock.json`. The `genesis stack` command triggers auto-installation as a second phase after generating the stack document.

### 4. Orchestration Layer

High-level workflows that combine the components above:

- **Business Workflow** (`genesis plan`) — takes a project idea, runs an AI-driven planning session, saves vision, market, product, business model, and OKRs to the `business` namespace
- **Stack Workflow** (`genesis stack`) — reads the business RAG context and user technology preferences, generates a comprehensive tech stack decision document saved to `knowledge/dev/stack.md`, then automatically queries skills.sh and installs relevant skills for every technology in the stack. If `stack.md` already exists, it is read as context and updated rather than replaced.
- **Ask Workflow** (`genesis ask`) — retrieves the most relevant documents from the RAG across any namespace and sends them as context to the LLM to answer natural language questions about the project
- **Task Engine** — generates, prioritizes, and tracks tasks from RAG context and business objectives *(Phase 3)*
- **Dev Workflow** — queries RAG before every implementation; writes code, ADRs, and documentation *(Phase 3)*
- **Infra Agent** — provisions infrastructure based on architecture decisions in the RAG *(Phase 4)*
- **Deploy Agent** — handles CI/CD pipelines and production deployments *(Phase 4)*
- **Journal** — every action by every agent is appended to `project_dev_log.md`; this log is the single source of truth for all decisions

### 5. Project Registry

A lightweight configuration that connects a project to Genesis Engine:

```yaml
# genesis.yaml (in the consuming project)
project: my-game-list
mode: local          # "local" (prototype) | "hosted" (Phase 1)
knowledge_dir: knowledge
llm_routing:
  default: groq
  business: groq
  code: groq
  analysis: groq
```

That is the only Genesis Engine artifact inside a consuming project.

## CLI Commands

| Command | Description |
|---------|-------------|
| `genesis plan "<idea>"` | Generate business plan (5 sections → `knowledge/business/`) |
| `genesis stack ["<preferences>"]` | Generate tech stack document + auto-install skills from skills.sh |
| `genesis ask "<question>"` | RAG-backed Q&A — retrieves context, answers via LLM |
| `genesis query "<query>"` | Raw RAG search — returns scored document list |
| `genesis read <theme>` | Print full content of an external skill theme |
| `genesis namespaces` | List loaded namespaces |

## Data Flow

```
User describes idea
      │
      ▼
genesis plan → Business Workflow
      │  saves vision, market, product, OKRs to business namespace
      ▼
genesis stack → Stack Workflow
      │  reads business context → generates stack.md → saves to dev namespace
      │  → Skills Manager → fetches skills from skills.sh → saves to external namespace
      ▼
Development begins
      │  agent reads RAG before every decision (genesis ask / genesis query)
      ▼
Journal → logs everything to project_dev_log.md
      │  (future: re-ingested into RAG after each session)
      ▼
Task Engine → Dev Workflow → Infra/Deploy Agent  [Phase 3–4]
```

## Current Implementation State

| Component | Status |
|-----------|--------|
| Local RAG (nomic embeddings, chunking, disk cache) | ✅ Done |
| CLI — `query`, `read`, `namespaces` | ✅ Done |
| ProjectJournal (append-only log) | ✅ Done |
| Agent Connector (OpenAI, Gemini, DeepSeek, Groq) | ✅ Done |
| Business Workflow (`genesis plan`) | ✅ Done |
| Stack Workflow (`genesis stack`) + auto skill install | ✅ Done |
| Ask Workflow (`genesis ask`) | ✅ Done |
| Skills ingestion from skills.sh | ✅ Done |
| Hosted RAG Service (Supabase pgvector) | 🔲 Phase 1 |
| Task Engine | 🔲 Phase 3 |
| Dev Workflow (autonomous coding) | 🔲 Phase 3 |
| Infra / Deploy Agent | 🔲 Phase 4 |
