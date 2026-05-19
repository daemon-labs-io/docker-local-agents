# 🤖 Autonomous Agents: Building Your Local AI Crew

## 🛑 Prerequisites

Work through the three steps below in order before starting the workshop itself.

### General prerequisites

Make sure your environment is set up by following our general prerequisites documentation:

➡️ **[Prerequisites guide](https://github.com/daemon-labs-io/prerequisites)**

### Get the workshop code

#### Open a terminal window

- **macOS:** open Spotlight (Cmd+Space), type "Terminal", press Enter.
- **Windows:** press the Windows key, type "Windows Terminal" (or "PowerShell"), press Enter. If you're using WSL, open your WSL distribution instead so paths and permissions behave as expected.
- **Linux:** Ctrl+Alt+T on most desktops, or open your distribution's terminal emulator of choice.

#### Navigate to your repositories folder

We recommend creating a `daemon-labs` folder in your home directory so everyone in the room is working from the same place (and any future Daemon workshop repos live alongside this one):

- **macOS / Linux / WSL**

  ```shell
  mkdir -p ~/daemon-labs && cd ~/daemon-labs
  ```

- **Windows PowerShell**

  ```shell
  mkdir $HOME\daemon-labs -Force; cd $HOME\daemon-labs
  ```

> [!TIP]
> Prefer to keep your own convention? `cd` into whichever folder you normally use for repositories — the rest of the workshop works the same either way.

#### Clone this repository

```shell
git clone https://github.com/daemon-labs-io/docker-local-agents.git
```

#### Open the folder in your code editor

```shell
code ./docker-local-agents
```

> [!WARNING]
> If this command doesn't work, open Visual Studio Code → open the Command Palette (Cmd+Shift+P on macOS, Ctrl+Shift+P on Windows/Linux) → type "Install 'code' command in PATH" → press Enter.

<!--  -->

> [!TIP]
> With Visual Studio Code open, you can do everything else from within the editor.  
> Open the terminal pane via Terminal → New Terminal.

### Workshop-specific prerequisites

Choose the path that matches how you're taking the workshop:

- **At an in-person workshop?** Follow the [in-person workshop prerequisites](./prerequisites/WORKSHOP.md).
- **Working through this on your own (at home or at work)?** Follow the [individual prerequisites](./prerequisites/INDIVIDUAL.md).

---

## 1. Setup & start services

**Goal:** Start the services from the previous workshops, ready to build agents.

### Navigate to the workshop directory

The `workshop/` directory contains the Docker Compose file, Modelfiles, and Python scripts from the previous workshops:

```shell
cd ./workshop
```

### Start services and install dependencies

Start the Docker services:

```shell
docker compose up -d
```

> [!NOTE]  
> The `python` service uses a Docker profile so it only runs on demand, it won't start with `docker compose up`.

Verify all services are running:

```shell
docker compose ps
```

Import models from local files:

```shell
docker compose exec ollama ollama create phi3:mini -f /root/workshop/Modelfile.phi3
```

```shell
docker compose exec ollama ollama create nomic-embed-text -f /root/workshop/Modelfile.nomic-embed-text
```

> [!TIP]
> **Hardware tier expectations:** `phi3:mini` is around 2.4 GB and runs comfortably on 8 GB CPU-only laptops with responsive inference times (8-15 seconds per task). GPU-accelerated machines (Apple Silicon, Nvidia) will be faster but the workshop works well on CPU-only tier.

Verify models have been imported:

```shell
docker compose exec ollama ollama list
```

> [!NOTE]
> You should see `phi3:mini` and `nomic-embed-text` listed.  
> We use `phi3:mini` because it balances model quality with fast inference on CPU-only machines, completing agent tasks in 8-15 seconds.

Install Python dependencies:

```shell
docker compose run --rm python pip install -r src/requirements.txt
```

> [!NOTE]
> This installs the dependencies needed to ingest and embed the sample documents. We'll add CrewAI in the next section.

Ingest documents and generate embeddings:

```shell
docker compose run --rm python python src/ingest.py
```

> [!NOTE]  
> You should see:
>
> ```text
> Loading documents...
> Loaded 3 documents
> Chunking documents...
> Created X chunks
> ```

```shell
docker compose run --rm python python src/embed.py
```

> [!NOTE]  
> You should see:
>
> ```text
> Loading documents...
> Chunking documents...
> Created X chunks
> Generating embeddings...
> Stored X embeddings in ChromaDB
> Done!
> ```

---

## 2. Your first agent

**Goal:** Build a single agent with no tools. See it reason through a task.

### Install CrewAI

Add CrewAI and its tools package to `workshop/src/requirements.txt`:

```text
chromadb>=0.5.0
langchain-text-splitters>=0.3.0
requests>=2.31.0
crewai>=0.86.0
crewai-tools>=0.17.0
```

Install the updated dependencies:

```shell
docker compose run --rm python pip install -r src/requirements.txt
```

> [!NOTE]
> CrewAI pulls in a lot of transitive dependencies. Expect this to take 2 to 3 minutes on first run.

### Create the first agent

Create the basic agent file:

```text
workshop/src/agent_basic.py
```

And add the following:

```python
import time
import sys
from pathlib import Path

from crewai import Agent, Task, Crew, LLM

sys.path.insert(0, str(Path(__file__).parent))
import config

llm = LLM(
    model=f"ollama/{config.GENERATION_MODEL}",
    base_url=config.OLLAMA_BASE_URL,
)

researcher = Agent(
    role="Researcher",
    goal="Produce clear, well-structured summaries on technical topics",
    backstory=(
        "You are a meticulous researcher who breaks down complex topics into "
        "plain language. You value clarity over cleverness."
    ),
    llm=llm,
    verbose=True,
)

task = Task(
    description=(
        "Explain what Retrieval-Augmented Generation (RAG) is, why it matters, "
        "and in what scenarios it should be used instead of a plain LLM."
    ),
    expected_output="A 3-paragraph summary suitable for a technical audience.",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task], verbose=True)

if __name__ == "__main__":
    print("🟢 Starting crew execution...", flush=True)
    sys.stdout.flush()

    start_time = time.time()
    result = crew.kickoff()
    elapsed = time.time() - start_time

    print(f"\n✅ Completed in {elapsed:.1f} seconds\n")
    print("=== RESULT ===\n")
    print(result)
```

### Run the basic agent

```shell
docker compose run --rm python python src/agent_basic.py
```

> [!NOTE]
> Watch the `verbose=True` output closely. You should see:
>
> - The agent's role and goal printed
> - The task it receives
> - A "Final Answer" it produces
>
> This is an agent reasoning through one task with no tools yet.

<!--  -->

> [!TIP]
> With `phi3:mini`, expect 8-15 seconds per task. The timing is printed at the end of execution.

---

## 3. Enhanced context: Providing knowledge to agents

**Goal:** Show how agents reason over provided context. This demonstrates the information retrieval pattern without tool calling.

### Create an agent with knowledge context

Create `src/agent_with_rag_context.py`:

```python
import sys
from pathlib import Path

import requests
import chromadb
from crewai import Agent, Task, Crew, LLM

sys.path.insert(0, str(Path(__file__).parent))
import config


def get_embedding(text: str) -> list[float]:
    """Generate an embedding for a text query."""
    response = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": config.EMBEDDING_MODEL, "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


def search_knowledge_base(query: str, n_results: int = 3) -> str:
    """Search the knowledge base and return formatted results."""
    client = chromadb.HttpClient(host=config.CHROMA_HOST, port=8000)
    collection = client.get_collection(name=config.COLLECTION_NAME)
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=n_results)

    chunks = results.get("documents", [[]])[0]
    sources = [m.get("source", "unknown") for m in results.get("metadatas", [[]])[0]]

    if not chunks:
        return "No relevant information found in knowledge base."

    formatted = "=== KNOWLEDGE BASE RESULTS ===\n\n"
    for i, (source, chunk) in enumerate(zip(sources, chunks), 1):
        formatted += f"[{i}] From {source}:\n{chunk}\n\n"

    return formatted


llm = LLM(
    model=f"ollama/{config.GENERATION_MODEL}",
    base_url=config.OLLAMA_BASE_URL,
)

support_agent = Agent(
    role="Support Specialist",
    goal="Answer user questions accurately using the provided knowledge base excerpts",
    backstory=(
        "You are a helpful support specialist. You answer questions by carefully reading "
        "the provided knowledge base excerpts. You cite the source of every fact. "
        "If the knowledge base doesn't contain the answer, you say so honestly."
    ),
    llm=llm,
    verbose=True,
)

if __name__ == "__main__":
    question = "What are the hardware requirements?"

    print(f"📚 Searching knowledge base for: '{question}'\n")

    # Retrieve relevant context upfront
    knowledge_context = search_knowledge_base(question, n_results=3)

    print(knowledge_context)
    print("=" * 80)
    print("🤖 Agent analyzing knowledge base...\n")

    # Create task with context already included
    task = Task(
        description=(
            f"Based on the knowledge base excerpts below, answer this question: {question}\n\n"
            f"{knowledge_context}\n"
            f"Remember to cite which source each fact comes from."
        ),
        expected_output="A clear answer with sources cited in [source: filename] format.",
        agent=support_agent,
    )

    crew = Crew(agents=[support_agent], tasks=[task], verbose=True)

    result = crew.kickoff()
    print("\n=== FINAL ANSWER ===\n")
    print(result)
```

### Run the context-aware agent

```shell
docker compose run --rm python python src/agent_with_rag_context.py
```

> [!NOTE]
> Observe the full pipeline:
>
> 1. **Retrieval**: Knowledge base is searched (you see the excerpts)
> 2. **Context provision**: Results are given to the agent
> 3. **Reasoning**: Agent reasons over the provided context
> 4. **Citation**: Agent cites sources in its answer
>
> This is how RAG works at its core: retrieve relevant context, provide it to the agent, let the agent reason over it. No tool calling needed.

---

## 4. Knowledge augmentation: Multi-agent reasoning with RAG

**Goal:** Build a multi-agent crew where agents collaborate, with both agents reasoning over pre-retrieved knowledge base context.

This section extends the RAG pattern to a **multi-agent workflow**: a Researcher agent gathers facts, and an Editor agent transforms them into polished prose. Both work with the same retrieved knowledge base context.

### Build a multi-agent crew with shared context

Create `src/crew_with_rag_context.py`:

```python
import sys
from pathlib import Path

import requests
import chromadb
from crewai import Agent, Task, Crew, LLM, Process

sys.path.insert(0, str(Path(__file__).parent))
import config


def get_embedding(text: str) -> list[float]:
    """Generate an embedding for a text query."""
    response = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": config.EMBEDDING_MODEL, "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


def search_knowledge_base(query: str, n_results: int = 3) -> str:
    """Search the knowledge base and return formatted results."""
    client = chromadb.HttpClient(host=config.CHROMA_HOST, port=8000)
    collection = client.get_collection(name=config.COLLECTION_NAME)
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=n_results)

    chunks = results.get("documents", [[]])[0]
    sources = [m.get("source", "unknown") for m in results.get("metadatas", [[]])[0]]

    if not chunks:
        return "No relevant information found in knowledge base."

    formatted = "=== KNOWLEDGE BASE RESULTS ===\n\n"
    for i, (source, chunk) in enumerate(zip(sources, chunks), 1):
        formatted += f"[{i}] From {source}:\n{chunk}\n\n"

    return formatted


llm = LLM(
    model=f"ollama/{config.GENERATION_MODEL}",
    base_url=config.OLLAMA_BASE_URL,
)

researcher = Agent(
    role="Researcher",
    goal="Gather accurate facts from the knowledge base and organize them",
    backstory="You are a meticulous researcher who finds facts and cites sources. You never speculate.",
    llm=llm,
    verbose=True,
)

editor = Agent(
    role="Editor",
    goal="Turn research notes into a polished, reader-friendly briefing",
    backstory=(
        "You take raw research notes and shape them into clear prose for a technical audience. "
        "You preserve every source citation from the original research."
    ),
    llm=llm,
    verbose=True,
)

if __name__ == "__main__":
    topic = "security and password policy"

    print(f"📚 Searching knowledge base for: '{topic}'\n")

    # Retrieve context once, use for both agents
    knowledge_context = search_knowledge_base(topic, n_results=5)

    print(knowledge_context)
    print("=" * 80)
    print("🤖 Crew execution starting...\n")

    research_task = Task(
        description=(
            f"Research the following topic using the provided knowledge base: {topic}\n\n"
            f"{knowledge_context}\n"
            f"Organize your findings as a bulleted list with [source: filename] citations."
        ),
        expected_output="A bulleted list of facts with [source: filename] citations.",
        agent=researcher,
    )

    editing_task = Task(
        description="Turn the research notes into a polished 2-paragraph briefing.",
        expected_output="A 2-paragraph briefing with sources preserved.",
        agent=editor,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, editor],
        tasks=[research_task, editing_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    print("\n=== FINAL BRIEFING ===\n")
    print(result)
```

### Run the multi-agent crew

```shell
docker compose run --rm python python src/crew_with_rag_context.py
```

> [!NOTE]
> Watch the workflow:
>
> 1. **Knowledge retrieval**: Results are fetched and displayed
> 2. **Researcher task**: Agent gathers facts with source citations
> 3. **Editor task**: Receives researcher notes and polishes them into prose
> 4. **Final output**: A polished 2-paragraph briefing with citations preserved
>
> This demonstrates sequential multi-agent collaboration with shared context.

---

## 5. Human-in-the-loop: Approval gates for agent actions

**Goal:** Add a human approval gate so you review the Researcher's output before the Editor acts on it.

Autonomous doesn't have to mean unsupervised. CrewAI lets you drop a human gate onto any task with a single flag. This is your panic handbrake.

### Build a gated crew with context injection

Create `src/crew_hitl.py`:

```python
import sys
from pathlib import Path

import requests
import chromadb
from crewai import Agent, Task, Crew, LLM, Process

sys.path.insert(0, str(Path(__file__).parent))
import config


def get_embedding(text: str) -> list[float]:
    """Generate an embedding for a text query."""
    response = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": config.EMBEDDING_MODEL, "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


def search_knowledge_base(query: str, n_results: int = 3) -> str:
    """Search the knowledge base and return formatted results."""
    client = chromadb.HttpClient(host=config.CHROMA_HOST, port=8000)
    collection = client.get_collection(name=config.COLLECTION_NAME)
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=n_results)

    chunks = results.get("documents", [[]])[0]
    sources = [m.get("source", "unknown") for m in results.get("metadatas", [[]])[0]]

    if not chunks:
        return "No relevant information found in knowledge base."

    formatted = "=== KNOWLEDGE BASE RESULTS ===\n\n"
    for i, (source, chunk) in enumerate(zip(sources, chunks), 1):
        formatted += f"[{i}] From {source}:\n{chunk}\n\n"

    return formatted


llm = LLM(
    model=f"ollama/{config.GENERATION_MODEL}",
    base_url=config.OLLAMA_BASE_URL,
)

researcher = Agent(
    role="Researcher",
    goal="Gather accurate facts from the knowledge base and organize them",
    backstory="You are a meticulous researcher who finds facts and cites sources. You never speculate.",
    llm=llm,
    verbose=True,
)

editor = Agent(
    role="Editor",
    goal="Turn research notes into a polished, reader-friendly briefing",
    backstory=(
        "You take raw research notes and shape them into clear prose for a technical audience. "
        "You preserve every source citation from the original research."
    ),
    llm=llm,
    verbose=True,
)

if __name__ == "__main__":
    topic = "security and password policy"

    print(f"📚 Searching knowledge base for: '{topic}'\n")

    # Retrieve context once, use for both agents
    knowledge_context = search_knowledge_base(topic, n_results=5)

    print(knowledge_context)
    print("=" * 80)
    print("🤖 Crew execution starting...\n")

    research_task = Task(
        description=(
            f"Research the following topic using the provided knowledge base: {topic}\n\n"
            f"{knowledge_context}\n"
            f"Organize your findings as a bulleted list with [source: filename] citations."
        ),
        expected_output="A bulleted list of facts with [source: filename] citations.",
        agent=researcher,
        human_input=True,  # <-- Pause for human approval after research
    )

    editing_task = Task(
        description="Turn the research notes into a polished 2-paragraph briefing.",
        expected_output="A 2-paragraph briefing with sources preserved.",
        agent=editor,
        context=[research_task],
    )

    crew = Crew(
        agents=[researcher, editor],
        tasks=[research_task, editing_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    print("\n=== FINAL BRIEFING ===\n")
    print(result)
```

### Run the gated crew

```shell
docker compose run --rm python python src/crew_hitl.py
```

> [!NOTE]
> After the Researcher produces its draft, CrewAI will pause and prompt you in the terminal. You have three options:
>
> 1. Press Enter to accept the output as it stands
> 2. Type corrections or additional instructions to refine the output before handoff
> 3. Press Ctrl+C to abort the entire crew
>
> The Editor only runs once you've signed off on the research.

<!--  -->

> [!WARNING]
> If the prompt appears but you can't type into it, your terminal might not have an attached TTY. Try rerunning with `docker compose run --rm -it python python src/crew_hitl.py`.

<!--  -->

> [!TIP]
> In production you'd replace the terminal prompt with a Slack message, a ticket, or an email approval. The primitive is identical: the task halts until a human responds. This is the difference between an agent that helps and an agent that runs away.

---

---

## 6. Cleanup

**Goal:** Tidy up resources and reclaim disk space.

Stop and remove containers, volumes, and images built by the project:

```shell
docker compose down -v --rmi local
```

Verify nothing is left behind:

```shell
docker compose ps -a
```

> [!TIP]
> If you want to keep the models for future workshops, run `docker compose down` without `-v` and they'll persist in the named volume.

---

## 🎉 Congratulations

You've taken your local AI stack from answering questions to building reasoning agents, all under your control.

✅ **Built** a single agent that reasons through a task  
✅ **Connected** agents to your private knowledge base via RAG with context injection  
✅ **Composed** multiple agents into a collaborating Researcher + Editor crew  
✅ **Added** a human-in-the-loop approval gate so the crew never runs away  
✅ **Ran** the whole thing air-gapped, with nothing leaving your machine

### Where to go next

| Topic                      | Tool / Approach                                 |
| -------------------------- | ----------------------------------------------- |
| Tool binding               | Add CrewAI tools to agents (with larger models) |
| Evaluating agent behaviour | Promptfoo with agent trajectories               |
| Hierarchical crews         | CrewAI `Process.hierarchical` + manager agent   |
| Graph-based workflows      | LangGraph for stateful, branching agents        |
| Production observability   | Self-hosted Langfuse for agent tracing          |
