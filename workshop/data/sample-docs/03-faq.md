# Frequently Asked Questions

## Why local instead of cloud?

Local AI keeps your data on your machine.
It's the right choice when privacy, regulation, or cost matters.
Cloud is still better for very large models or bursty workloads.

## Why CrewAI?

CrewAI is opinionated enough to get a working multi-agent system running in minutes.
It has role-based agents that map naturally onto team structures.
Alternatives include LangGraph, which is more flexible with a steeper learning curve, and AutoGen, which is broader but less focused on crews.

## Why phi3:mini?

It balances model quality with fast inference on CPU-only machines (~2.4 GB quantised). On 8 GB machines, agent tasks complete in 8-15 seconds with good reasoning quality.
The workshop uses context injection for RAG instead of tool calling, so model choice focuses on inference speed and reasoning quality rather than tool-calling capability.
For richer reasoning on more capable hardware, `phi3` (full-size) or `mistral` are solid steps up.

## Why ChromaDB?

Simple to run locally, good enough for workshop-scale data, runs happily in a Docker container.
For production you might choose pgvector, Qdrant, or a hosted service.

## Can I bring my own documents?

Yes.
Drop Markdown files into `workshop/data/sample-docs/`, then rerun `python src/ingest.py` and `python src/embed.py`.
The agents will pick them up via RAG context injection in their task descriptions.

## Can I use different models?

Yes.
Edit `src/config.py` to change `GENERATION_MODEL` or `EMBEDDING_MODEL`.
Make sure the model is available in Ollama first via `docker compose exec ollama ollama pull <model-name>`.

## The agents are slow on my laptop. What can I do?

With `phi3:mini`, 8-15 seconds per agent turn on CPU-only machines is expected.
Options if you want faster inference:

- Use a GPU (Apple Silicon or Nvidia) if available
- Increase your Docker Desktop memory allocation in Settings → Resources
- Use a quantized version with lower precision (faster, slightly less accurate)

## Can I trust the agent's output?

Only as much as you trust the model plus the retrieved context.
Always keep a human in the loop for anything that has real-world consequences.
See section 5 of the workshop for the human-in-the-loop approval gate pattern.
