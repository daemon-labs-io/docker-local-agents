# Welcome to the Local AI Workshop System

This document introduces the local AI workshop system and the hardware you'll need to run it.

## What this system is

A local AI stack running on your own machine. You get:

- An LLM for generation (`qwen2.5:1.5b` via Ollama)
- An embedding model (`nomic-embed-text` via Ollama)
- A vector database (ChromaDB) for semantic search
- Orchestration via Python scripts and CrewAI

Everything runs air-gapped. No cloud APIs, no API keys, no data leaving your machine.

## Hardware requirements

- **RAM:** 8 GB minimum, 16 GB recommended
- **Disk space:** 10 GB free
- **Docker:** Docker Desktop or an equivalent such as Rancher Desktop, installed and running
- **GPU (optional):** Apple Silicon or Nvidia GPUs will significantly speed up inference

## What is RAG?

Retrieval-Augmented Generation (RAG) is a pattern for giving an LLM access to documents it wasn't trained on. When a user asks a question, the system:

1. Converts the question to a vector using an embedding model
2. Searches a vector database for the most semantically similar document chunks
3. Sends those chunks plus the question to the LLM
4. The LLM generates an answer grounded in the retrieved content

RAG is preferred over fine-tuning when the knowledge changes frequently, when you need citations back to source documents, or when you want to keep data private and local.

## Getting started

If you're following a workshop, return to the readme for step-by-step instructions.
