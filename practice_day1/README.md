# Practice Day 1: Building a Coding Agent

## Goal

Build an AI agent that can analyze a Python codebase — read files, search code,
review git history, and remember context across turns.

## Setup (5 min)

### 1. Install uv (if not installed)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install dependencies

```bash
# From the workshop root directory
uv sync
```

### 3. Set up API key

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

## Project Structure

```
practice_day1/
├── config.py              # Shared config (REPO_PATH)
├── prompts.py             # System prompt for the agent
├── tools.py               # ⭐ YOUR FILE — implement the 3 tools
├── agent.py               # ⭐ YOUR FILE — wire up the LangGraph agent
├── chat.py                # Interactive chat (uses solution_agent by default)
├── solution_tools.py      # Full solution (don't peek until you're done!)
└── solution_agent.py      # Full solution (don't peek until you're done!)
```

## Task (25 min)

| Step | Where       | What to do                                                      | Time   |
|------|-------------|-----------------------------------------------------------------|--------|
| 1    | `agent.py`  | **State** — already done for you                                | —      |
| 2    | `tools.py`  | **Tools** — implement `get_file_content`, `search_codebase`, `get_git_diff` | 15 min |
| 3    | `agent.py`  | **LLM + chatbot node** — `ChatOpenAI`, `bind_tools`, chatbot fn | 3 min  |
| 4    | `agent.py`  | **Graph** — connect nodes and edges                             | 5 min  |
| 5    | `agent.py`  | **Checkpointer** — add `MemorySaver` so the agent remembers     | 2 min  |

## Testing Your Agent

By default `chat.py` imports from `solution_agent.py` so the starter UI works
out of the box. Once you finish your own `agent.py`, switch the import:

```python
# in chat.py
from agent import graph   # was: from solution_agent import graph
```

Then run:

```bash
uv run python practice_day1/chat.py
```

Pass a `thread_id` in the config when you invoke the graph — the checkpointer
uses it to separate conversations:

```python
config = {"configurable": {"thread_id": "1"}}
graph.invoke({"messages": [...]}, config=config)
```

## Demo Queries to Try

1. **Architecture overview** — "What does this project do? Look at the main
   files and describe the architecture."
2. **Bug hunt** — "Find any bugs in the codebase. Check the utility functions
   carefully." (there's a real one in `sample_repo/utils.py`)
3. **PR summary** — "Show me the git diff between HEAD~4 and HEAD and write a
   PR summary."
4. **Follow-up (tests your checkpointer)** — after any of the above, ask:
   "And now show me a different file from the same module." If the agent
   remembers which module you meant, your `thread_id` is wired correctly.

## Bonus Challenges

If you finish early:

1. **Add a new tool** in `tools.py`: `list_files()` — returns all files in the repo
2. **Stream tool calls** — print each `AIMessage` / `ToolMessage` as it happens
   instead of just the final answer
3. **Swap checkpointer** — replace `MemorySaver` (in-memory) with
   `SqliteSaver` so conversations survive process restarts
