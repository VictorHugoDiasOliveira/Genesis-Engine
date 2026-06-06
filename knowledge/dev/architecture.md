# Genesis Engine Architecture

## Overview
Genesis-Engine will be an AI-driven development orchestration platform focused on:

- Strategic and business planning
- Task and decision management
- Agent-assisted code development
- Continuous documentation and project history updates
- Use of RAG (Retrieval-Augmented Generation) to access relevant knowledge

## Core Components

1. Knowledge Base (RAG)
   - Technical development documents
   - Business planning documents
   - External sources (Skills.sh, ADRs, business rules, history)
   - Vector database for semantic search

2. AI Agents and Pipeline
   - Claude Code as the primary implementation agent
   - Planning and review agents
   - RAG query process before generating code or making decisions

3. Development Log
   - `project_dev_log.md` as the single source of truth
   - History of implementations, architectural decisions, and tasks
   - Automated update by the agent after each change

4. Task Orchestration
   - Task generation from RAG queries and results
   - Planning adjustment based on business objectives
   - Continuous prioritization and goal evolution

## Workflow

1. The agent queries the RAG to understand context and constraints.
2. The agent uses the results to define tasks, architecture, and implementation.
3. Code and documentation are generated or updated.
4. The agent records a summary of changes and decisions in `project_dev_log.md`.
5. The project evolves with historical memory and business information.
