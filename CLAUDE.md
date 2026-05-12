# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Workshop repository for "Autonomous Agents: Building Your Local AI Crew" — a hands-on tutorial that builds local AI agents using CrewAI, Ollama, and ChromaDB, all running via Docker Compose. Everything runs air-gapped; nothing leaves the user's machine.

## Architecture

Three Docker services defined in `workshop/docker-compose.yaml`:

- **ollama** — local LLM inference (phi3:mini for generation, nomic-embed-text for embeddings), port 11434
- **chromadb** — vector database for RAG, port 8000
- **python** — runs on-demand via a Docker profile (`--profile python`), not started by `docker compose up`

The `python` service mounts `workshop/` to `/app` and uses environment variables `OLLAMA_BASE_URL=http://ollama:11434` and `CHROMA_HOST=chromadb` for inter-service communication.

Models are imported from local GGUF files via Modelfiles, not pulled from the internet.

## Key Paths

- `workshop/src/config.py` — shared constants (model names, chunk sizes, collection name, service URLs)
- `workshop/src/ingest.py` — loads markdown docs from `workshop/data/sample-docs/`, chunks them with langchain-text-splitters
- `workshop/src/embed.py` — generates embeddings via Ollama API, stores in ChromaDB collection `workshop-docs`
- `workshop/data/sample-docs/` — sample markdown documents for the RAG pipeline
- `workshop/Modelfile.*` — Ollama Modelfiles referencing local GGUF weights

## Commands

All commands run from the `workshop/` directory.

```shell
# Start services (ollama + chromadb)
docker compose up

# Import models into Ollama
docker compose exec ollama ollama create phi3:mini -f /root/workshop/Modelfile.phi3
docker compose exec ollama ollama create nomic-embed-text -f /root/workshop/Modelfile.nomic-embed-text

# Install Python dependencies
docker compose run --rm python pip install -r src/requirements.txt

# Run data pipeline
docker compose run --rm python python src/ingest.py
docker compose run --rm python python src/embed.py

# Run agent scripts
docker compose run --rm python python src/agent_basic.py
docker compose run --rm python python src/agent_with_rag_context.py
docker compose run --rm python python src/crew_with_rag_context.py
docker compose run --rm python python src/crew_hitl.py

# Cleanup
docker compose down -v --rmi local
```

## CI

Linting runs on pull requests via a reusable workflow from `daemon-labs-io/.github`. The required status check is `linting / Linting`.

## Git Workflow

- Default branch: `main`
- PRs require 1 approval, code owner review, and passing linting status checks
- Squash merge is the preferred merge method (branch deleted on merge)

## .gitignore Note

The `.gitignore` uses an allowlist pattern — it ignores everything (`*`) then explicitly un-ignores specific paths. When adding new top-level directories or file types, you must add a corresponding `!` entry.
