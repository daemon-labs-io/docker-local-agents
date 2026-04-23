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

**macOS / Linux / WSL**

```shell
mkdir -p ~/daemon-labs && cd ~/daemon-labs
```

**Windows PowerShell**

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

### Install dependencies and start services

Start the Docker services:

```shell
docker compose up
```

> [!NOTE]  
> The `python` service uses a Docker profile so it only runs on demand, it won't start with `docker compose up`.

Verify all services are running:

```shell
docker compose ps
```

> [!TIP]  
> In Visual Studio Code, you can open a new terminal via Terminal → Split Terminal or the + button to run this command while docker compose up runs in the current terminal.

Import models from local files:

```shell
docker compose exec ollama ollama create llama3.2:1b -f /root/workshop/Modelfile.llama3.2
```

```shell
docker compose exec ollama ollama create nomic-embed-text -f /root/workshop/Modelfile.nomic-embed-text
```

> [!TIP]
> **Hardware tier expectations:** `llama3.2:1b` is around 1.3 GB and runs comfortably on 8 GB CPU-only laptops. GPU-accelerated machines (Apple Silicon, Nvidia) will be quicker but the workshop works fine on either tier.

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

### Verify everything is working

```shell
docker compose exec ollama ollama list
```

> [!NOTE]
> You should see `llama3.2:1b` and `nomic-embed-text` listed. We use `llama3.2:1b` because it's small enough for any laptop while being properly fine-tuned for tool calling, which is the heart of agent work.

---

## 2. Your first agent

**Goal:** Build a single agent with no tools. See it reason through a task.

### Install CrewAI

Add CrewAI and its tools package to `src/requirements.txt`:

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

Create `src/agent_basic.py`:

```python
import os
from crewai import Agent, Task, Crew, LLM

llm = LLM(
    model="ollama/llama3.2:1b",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
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
    result = crew.kickoff()
    print("\n=== RESULT ===\n")
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
> First runs can take 30 to 60 seconds while the model warms up. Subsequent runs are faster.

---

## 3. Tool binding: your filesystem

**Goal:** Give the agent tools that read from your local filesystem and watch it decide when to use them.

### Create an agent with filesystem tools

Create `src/agent_with_filesystem.py`:

```python
import os
from pathlib import Path
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

llm = LLM(
    model="ollama/llama3.2:1b",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)

SAMPLE_DOCS = Path("/app/data/sample-docs")


@tool("List Sample Documents")
def list_documents() -> str:
    """List every markdown file available in the sample documents directory."""
    files = sorted(f.name for f in SAMPLE_DOCS.glob("*.md"))
    return "\n".join(files) if files else "No documents found."


@tool("Read Document")
def read_document(filename: str) -> str:
    """Read the full contents of a named document from the sample documents directory."""
    path = SAMPLE_DOCS / filename
    if not path.exists():
        return f"File not found: {filename}"
    return path.read_text(encoding="utf-8")


analyst = Agent(
    role="Document Analyst",
    goal="Produce accurate summaries of local documents",
    backstory=(
        "You are a precise analyst. You always list the available documents first, "
        "then read the ones relevant to your task before summarising. You never "
        "invent content that isn't in the document."
    ),
    llm=llm,
    tools=[list_documents, read_document],
    verbose=True,
)

task = Task(
    description="Summarise the welcome document for a new user of this system.",
    expected_output="A 3-bullet summary of the welcome document.",
    agent=analyst,
)

crew = Crew(agents=[analyst], tasks=[task], verbose=True)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n=== RESULT ===\n")
    print(result)
```

### Run the filesystem agent

```shell
docker compose run --rm python python src/agent_with_filesystem.py
```

> [!NOTE]
> Watch the verbose output. You should see the agent:
>
> 1. Call `List Sample Documents` to discover what's available
> 2. Call `Read Document` on the welcome file
> 3. Produce its summary from the actual file contents
>
> This is tool composition: the agent decides the order of tool calls based on the task.

<!--  -->

> [!WARNING]
> Small models sometimes skip `list_documents` and guess a filename. If the agent fails to find the file, run it again. For production use, you'd add a system prompt or tool description that forces the list-then-read pattern.

---

## 4. Tool binding: local APIs

**Goal:** Go beyond the filesystem. Give the agent a tool that calls a local HTTP API, in this case the ChromaDB knowledge base.

The filesystem tools in section 3 only work when you know exactly which file to read. Real agents often need to **search** rather than **fetch**. That's what a RAG tool does: it wraps a local API call (ChromaDB) behind a single semantic search function the agent can call.

### Add a RAG tool

Create `src/agent_with_rag.py`:

```python
import os
import requests
import chromadb
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

llm = LLM(
    model="ollama/llama3.2:1b",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)


def get_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{os.environ['OLLAMA_BASE_URL']}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


@tool("Search Knowledge Base")
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base and return the most relevant excerpts."""
    client = chromadb.HttpClient(host=os.environ["CHROMA_HOST"], port=8000)
    collection = client.get_collection(name="workshop-docs")
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=3)

    chunks = results.get("documents", [[]])[0]
    sources = [m.get("source", "unknown") for m in results.get("metadatas", [[]])[0]]
    if not chunks:
        return "No results found."

    return "\n\n".join(
        f"[source: {source}]\n{chunk}" for source, chunk in zip(sources, chunks)
    )


support_agent = Agent(
    role="Support Specialist",
    goal="Answer user questions accurately using only the internal knowledge base",
    backstory=(
        "You are a support specialist. You never guess. You always search the "
        "knowledge base first, and you cite the source of every fact."
    ),
    llm=llm,
    tools=[search_knowledge_base],
    verbose=True,
)

task = Task(
    description="Answer the following question using the knowledge base: {question}",
    expected_output="A clear answer with sources cited in [source: filename] format.",
    agent=support_agent,
)

crew = Crew(agents=[support_agent], tasks=[task], verbose=True)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"question": "What are the hardware requirements?"})
    print("\n=== RESULT ===\n")
    print(result)
```

### Run the RAG-enabled agent

```shell
docker compose run --rm python python src/agent_with_rag.py
```

> [!NOTE]
> In the verbose output, you should see the agent calling `Search Knowledge Base`, receiving excerpts, then weaving them into its final answer with source citations.

### Try different questions

Edit the `question` input in the script, or take a minute now to pick a question relevant to your own work and see how the agent handles it.

---

## 5. Building a crew

**Goal:** Two agents, each with a distinct role, collaborating on a multi-step task.

### Create a multi-agent crew

Create `src/crew.py`:

```python
import os
import requests
import chromadb
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import tool

llm = LLM(
    model="ollama/llama3.2:1b",
    base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
)


def get_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{os.environ['OLLAMA_BASE_URL']}/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


@tool("Search Knowledge Base")
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base and return the most relevant excerpts."""
    client = chromadb.HttpClient(host=os.environ["CHROMA_HOST"], port=8000)
    collection = client.get_collection(name="workshop-docs")
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=3)
    chunks = results.get("documents", [[]])[0]
    sources = [m.get("source", "unknown") for m in results.get("metadatas", [[]])[0]]
    if not chunks:
        return "No results found."
    return "\n\n".join(
        f"[source: {source}]\n{chunk}" for source, chunk in zip(sources, chunks)
    )


researcher = Agent(
    role="Researcher",
    goal="Gather accurate facts from the knowledge base",
    backstory="You find facts. You cite sources. You never speculate.",
    llm=llm,
    tools=[search_knowledge_base],
    verbose=True,
)

editor = Agent(
    role="Editor",
    goal="Turn research notes into a polished, reader-friendly briefing",
    backstory=(
        "You take raw research notes and shape them into clear prose for a "
        "technical audience. You preserve every source citation from the original "
        "research."
    ),
    llm=llm,
    verbose=True,
)

research_task = Task(
    description="Research the following topic using the knowledge base: {topic}",
    expected_output="A bulleted list of facts with [source: filename] citations.",
    agent=researcher,
)

editing_task = Task(
    description="Turn the research notes into a polished briefing.",
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

if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "security and password policy"})
    print("\n=== RESULT ===\n")
    print(result)
```

### Run the crew

```shell
docker compose run --rm python python src/crew.py
```

> [!NOTE]
> Watch the handoff in the verbose output:
>
> 1. The Researcher runs first, uses the knowledge base, and produces a bulleted list of facts
> 2. The Editor receives those facts as context and produces the final prose
>
> This is the essence of a crew: different agents with different strengths, collaborating sequentially.

<!--  -->

> [!TIP]
> Try changing `Process.sequential` to `Process.hierarchical` and adding a `manager_llm` for a different collaboration pattern. (Save this for after the workshop as it needs additional setup.)

---

## 6. Human-in-the-loop

**Goal:** Add an approval gate so a human reviews the Researcher's output before the Editor acts on it.

Autonomous doesn't have to mean unsupervised. CrewAI lets you drop a human gate onto any task with a single flag. This is your panic handbrake.

### Add human approval to the research task

Copy `src/crew.py` to `src/crew_hitl.py`, then add `human_input=True` to the research task:

```python
research_task = Task(
    description="Research the following topic using the knowledge base: {topic}",
    expected_output="A bulleted list of facts with [source: filename] citations.",
    agent=researcher,
    human_input=True,  # <-- add this
)
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

## 7. Cleanup

**Goal:** Tidy up resources and reclaim disk space.

Stop any running containers by pressing **Ctrl+C** in the terminal where `docker compose up` is running.

Remove containers, volumes, and images built by the project:

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

You've taken your local AI stack from answering questions to taking action, under your control.

✅ **Built** a single agent that reasons through a task  
✅ **Bound** agents to tools on your filesystem and local APIs  
✅ **Connected** an agent to your private knowledge base via RAG  
✅ **Composed** two agents into a collaborating Researcher + Editor crew  
✅ **Added** a human-in-the-loop approval gate so the crew never runs away  
✅ **Ran** the whole thing air-gapped, with nothing leaving your machine

### Where to go next

| Topic                      | Tool / Approach                                  |
| -------------------------- | ------------------------------------------------ |
| More tools                 | Filesystem, web search (local only), Python REPL |
| Evaluating agent behaviour | Promptfoo with agent trajectories                |
| Hierarchical crews         | CrewAI `Process.hierarchical` + manager agent    |
| Graph-based workflows      | LangGraph for stateful, branching agents         |
| Production observability   | Self-hosted Langfuse for agent tracing           |
