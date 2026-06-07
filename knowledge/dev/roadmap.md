# Genesis Engine — Roadmap

## Current State (Prototype)

The local prototype is complete and functional:

- ✅ Semantic RAG with `nomic-embed-text-v1.5` (8192-token context, chunking, disk cache)
- ✅ Three knowledge namespaces: `dev`, `business`, `external`
- ✅ CLI for querying the knowledge base
- ✅ Skills ingestion from skills.sh
- ✅ `ProjectJournal` for append-only decision logging
- ✅ `CLAUDE.md`-driven agent workflow (Query → Implement → Log)

This prototype validates the core loop. The next phases turn it into a hosted platform.

---

## Phase 1 — Hosted RAG Service

**Goal:** Replace local markdown files + disk cache with a hosted vector database accessible via API.

- [ ] Set up Supabase pgvector schema (projects, namespaces, documents, embeddings)
- [ ] Implement `HostedVectorStore` that reads/writes to the remote DB
- [ ] `genesis init <project-name>` command — registers a project and creates its namespaces
- [ ] `genesis.yaml` project config (project ID, API key, LLM routing)
- [ ] Migrate existing local ingestion pipelines to write to the hosted store
- [ ] Keep local prototype working as fallback (offline / development mode)

**Exit criteria:** Running `python -m genesis_engine.cli query "..."` in any project hits the hosted RAG, not local files.

---

## Phase 2 — Agent Connector and Business Workflow

**Goal:** Allow Genesis Engine to call external LLMs, enriched with RAG context, and save the outputs back to the knowledge base.

- [ ] `AgentConnector` — unified client for OpenAI, Gemini, DeepSeek, and any OpenAI-compatible API
- [ ] Per-task LLM routing configured in `genesis.yaml`
- [ ] `BusinessWorkflow` — structured conversation flow:
  1. User describes the idea
  2. Genesis Engine asks clarifying questions (via chosen LLM)
  3. Generates mission, vision, target audience, business model, OKRs
  4. Saves everything to the `business` namespace
- [ ] `genesis plan <idea>` command — entry point for business planning

**Exit criteria:** `genesis plan "A game tracking platform like MyAnimeList"` produces a structured business plan saved to the hosted RAG.

---

## Phase 3 — Autonomous Skills Manager and Task Engine

**Goal:** Zero manual tooling in consuming projects. Genesis Engine decides what skills are needed, fetches them, and writes tasks autonomously.

- [ ] `SkillsManager` — queries skills.sh, evaluates relevance against project context, installs and ingests automatically
- [ ] Triggered before any new feature domain is started (e.g. when a React frontend is added, fetch React skills first)
- [ ] `TaskEngine` — generates, prioritizes, and tracks tasks from RAG context and business OKRs
- [ ] `genesis tasks` command — list pending tasks with RAG-sourced context
- [ ] `genesis task next` — pick and start the highest-priority task

**Exit criteria:** Starting a new feature domain triggers automatic skill discovery and task generation without human intervention.

---

## Phase 4 — Infra and Deploy Automation

**Goal:** Genesis Engine manages infrastructure provisioning and deployment pipelines.

- [ ] `InfraAgent` — generates Terraform / Pulumi configs from architecture decisions in the RAG
- [ ] `DeployAgent` — sets up CI/CD pipelines (GitHub Actions, etc.) and triggers deployments
- [ ] Deployment events logged to the `dev` namespace (what was deployed, when, what changed)
- [ ] `genesis deploy <env>` command

**Exit criteria:** `genesis deploy production` provisions infra (if needed) and deploys the project with no manual pipeline configuration.

---

## Beyond Phase 4

- **Multi-tenant platform** — one Genesis Engine instance serving multiple teams and projects
- **Skill marketplace** — community-contributed skills with quality ratings
- **Agent evaluation** — measure retrieval quality, task completion rate, and business alignment over time
- **Web dashboard** — visual view of project RAG, tasks, decisions, and deployment history
- **Fine-tuned routing** — learn from past projects which LLM performs best for which task types
