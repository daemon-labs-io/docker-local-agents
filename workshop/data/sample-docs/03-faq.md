# Frequently Asked Questions

## Why local instead of cloud?

Local AI keeps your data on your machine. It's the right choice when privacy, regulation, or cost matters. Cloud is still better for very large models or bursty workloads.

## Why CrewAI?

CrewAI is opinionated enough to get a working multi-agent system running in minutes. It has role-based agents that map naturally onto team structures. Alternatives include LangGraph, which is more flexible with a steeper learning curve, and AutoGen, which is broader but less focused on crews.

## Why llama3.2:1b?

It hits the sweet spot of being small (~1.3 GB quantised), so it downloads quickly over a venue network and runs on nearly any laptop including 8 GB CPU-only machines, while still being fine-tuned by Meta for function calling. That last bit matters: smaller models without function-calling training (such as tinyllama) frequently ignore tools and fabricate answers, which defeats the point of agent work. For richer reasoning on more capable hardware, `llama3.2:3b` is a solid step up.

## Why ChromaDB?

Simple to run locally, good enough for workshop-scale data, runs happily in a Docker container. For production you might choose pgvector, Qdrant, or a hosted service.

## Can I bring my own documents?

Yes. Drop markdown files into `workshop/data/sample-docs/`, then rerun `python src/ingest.py` and `python src/embed.py`. The agents will pick them up via the knowledge-base tool.

## Can I use different models?

Yes. Edit `src/config.py` to change `GENERATION_MODEL` or `EMBEDDING_MODEL`. Make sure the model is available in Ollama first via `docker compose exec ollama ollama pull <model-name>`.

## The agents are slow on my laptop. What can I do?

Expected behaviour on CPU-only machines. Options:

- Be patient, as 10 to 20 seconds per agent turn is normal
- Use a smaller model, but expect more tool-calling failures
- Increase your Docker Desktop memory allocation in Settings → Resources

## Can I trust the agent's output?

Only as much as you trust the model plus the retrieved context. Always keep a human in the loop for anything that has real-world consequences. See section 6 of the workshop.
