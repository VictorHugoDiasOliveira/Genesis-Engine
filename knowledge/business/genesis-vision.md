# Genesis Engine — Vision

## What Is Genesis Engine

Genesis Engine is an autonomous AI-driven development orchestration platform. It acts as the brain behind any software project — from the first business idea to production deployment — without requiring manual tooling inside the projects it manages.

Projects do not contain Genesis Engine. They connect to it.

## The Core Idea

Traditional development requires developers to manually manage context, make architectural decisions in isolation, set up tooling, and keep documentation in sync. Genesis Engine eliminates this by being the single intelligent layer that:

- Develops and validates the business idea through AI-driven conversations
- Maintains a hosted, always-current knowledge base (RAG) for each project
- Autonomously discovers and ingests best-practice skills before writing code
- Generates tasks, architecture decisions, and documentation from that knowledge
- Writes, reviews, and deploys code — consulting the RAG at every step
- Logs every decision so the system grows smarter over time

## How a Project Uses Genesis Engine

1. A user describes their idea to Genesis Engine (e.g. "I want to build MyGameList, a game tracking platform similar to MyAnimeList")
2. Genesis Engine opens a business planning session with the AI model of the user's choice (GPT, Gemini, DeepSeek, or others)
3. The resulting strategy, OKRs, and decisions are saved into the project's hosted RAG
4. When development begins, Genesis Engine finds and loads relevant skills into the RAG
5. All code generation, architectural decisions, and task creation happen through the RAG — no context is ever lost
6. Infrastructure and deployment are also handled autonomously

The consuming project contains only its own business logic and code. There are no local knowledge bases, no skill directories, no manual RAG configuration.

## Multi-LLM by Design

Genesis Engine is not tied to any single AI provider. Users choose which model powers each type of task:

| Task Type | Recommended Model | Why |
|-----------|-------------------|-----|
| Business planning | GPT-4 / Gemini | Strong structured reasoning |
| Long document analysis | Gemini | Large context window |
| Code generation | Any | User preference |
| Cost-sensitive iteration | DeepSeek | High capability, low cost |

The routing is configurable per project and per task type.

## Areas of Responsibility

- **Business** — vision, strategy, OKRs, go-to-market, competitive analysis
- **Product** — feature definition, prioritization, user stories
- **Architecture** — system design, ADRs, technology decisions
- **Engineering** — code generation, review, refactoring
- **Operations** — infrastructure, CI/CD, monitoring
- **Documentation** — always in sync, always in the RAG

## The Knowledge Loop

Every action Genesis Engine takes feeds back into the knowledge base:

```
Idea → Business Planning → RAG
RAG  → Task Generation  → Code
Code → Decisions logged → RAG (smarter for next task)
```

Nothing is ever lost. The system gets better with every project and every decision.
