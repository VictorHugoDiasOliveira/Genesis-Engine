# RAG Strategy for Genesis Engine

## Purpose of RAG
The RAG enables Claude Code and other agents to quickly access relevant knowledge before generating code, tasks, or decisions.

## Knowledge Bases

### 1. Development RAG

Content:
- Technical documents
- Architecture examples
- Code patterns
- ADRs and technical decisions
- Project history

Usage:
- Support for code implementation
- Choice of patterns and libraries
- Architectural review

### 2. Business Planning RAG

Content:
- Mission, vision, and values
- Business model
- Target audience and product
- Go-to-market strategy
- Internal rules and processes

Usage:
- Product priority definition
- Creating business-aligned tasks
- Strategic decision-making

## Proposed Structure

- `knowledge/dev/` — technical documents
- `knowledge/business/` — strategic documents
- `knowledge/external/` — sources such as Skills.sh

## Usage Rules

1. Always query the RAG before starting an implementation.
2. When context or history is needed, search across the technical and business namespaces.
3. Document the source and results used for each decision.

## Vector Database

- Implement a semantic search engine in Python.
- Store embeddings and metadata per document.
- Enable fast retrieval by query similarity.

## Expected Outcome

- More consistent agent implementations.
- Less rework due to missing context.
- Business planning aligned with development.
