# Practice Day 3: Multi-Agent PR Review Team

## Goal

Combine the Day 1 coding agent and the Day 2 RAG agent into a **multi-agent
system** that reviews pull requests: finds bugs, generates missing tests, and
checks coding standards — then assembles a single report.

## Setup (5 min)

Same as Day 1 / Day 2. If you already ran `uv sync` and configured `.env`,
skip this.

```bash
uv sync
cp .env.example .env   # add OPENAI_API_KEY
```

## Architecture

```
          ┌─────────────────┐
PR ────>  │   Coordinator   │   routes by PR size
          └────────┬────────┘
                   │
         ┌─────────┴──────────┐
       small                large
       (≤3 files)           (>3 files or tests)
         │                    │
         ▼              ┌─────┼─────┐
    Code Analyzer       │     │     │
    (Day 1)             ▼     ▼     ▼
         │         Code    Test   Standards
         │         (Day 1) (NEW)  (Day 2 RAG)
         │               └───┬───┘
         └─────────────┬─────┘
                       ▼
               ┌──────────────┐
               │   Report     │
               │  Assembler   │
               └──────┬───────┘
                      ▼
                📋 PR Report
```

**Key idea:** Code Analyzer = your Day 1 agent. Standards Agent = your Day 2
RAG agent. You import them as nodes — only Test Generator and Coordinator
are new.

The 3 agents on the right side run as a **true parallel fan-out** —
`decide_route` returns a list of node names, and LangGraph dispatches them
concurrently. Whichever nodes were scheduled converge at `report`.

### Two ways to compose an agent into the graph

We deliberately use **both patterns** in this day so you see the trade-offs:

| Pattern              | Where                            | What it looks like                                                         | When to reach for it |
|----------------------|----------------------------------|----------------------------------------------------------------------------|----------------------|
| **Explicit subgraph**    | `agents/code_analyzer.py`           | `StateGraph(CodeAnalyzerState)` with its own nodes, compiled and `add_node`'d to the parent | Multi-step internal logic, isolated state, reusable across pipelines, separate spans in LangSmith |
| **Agent-as-node**        | `agents/test_generator.py`, `agents/standards_agent.py` | Wrapper function that calls `react_agent.invoke(...)` and returns updates  | Single-step ReAct call, no internal state worth isolating, want minimal boilerplate |

The Code Analyzer subgraph has its own state schema (`CodeAnalyzerState`)
with shared keys (`pr_diff`, `files_changed`, `code_issues`, `messages`) plus
one *internal* key (`raw_response`) that the parent never sees — that's the
isolation benefit. LangGraph maps shared keys by name automatically when you
do `graph_builder.add_node("code_analyzer", code_analyzer_subgraph)`.

Both Test Generator and Standards Agent could be promoted to subgraphs
(see Bonus #6) — for now they stay as agent-as-node wrappers so you can
read the simpler version side-by-side.

## Project Structure

```
practice_day3/
├── config.py                          # Shared config (REPO_PATH, KNOWLEDGE_BASE_PATH, LLM_MODEL)
├── state.py                           # PRState — shared state all agents read/write
├── graph.py                           # ⭐ YOUR FILE — wire everything together
├── run.py                             # Entry point — runs the pipeline
├── report.py                          # Report assembler
├── solution_graph.py                  # Full solution — don't peek!
├── agents/
│   ├── coordinator.py                 # ⭐ YOUR FILE — routing logic
│   ├── test_generator.py              # ⭐ YOUR FILE — new agent with 3 tools
│   ├── solution_coordinator.py        # Full solution — don't peek!
│   ├── solution_test_generator.py     # Full solution — don't peek!
│   ├── code_analyzer.py               # ♻️ Day 1 agent — real LangGraph subgraph
│   └── standards_agent.py             # ♻️ Day 2 agent — agent-as-node (uses day2 RAG)
├── lib/
│   ├── prompts.py                     # Per-agent system prompts
│   └── json_utils.py                  # parse_json_from_response helper
└── debugging/                         # 3 break-and-fix scenarios (see below)
```

## Task (40 min)

The slide shows 5 blocks: **01** Coordinator · **02** Code Analyzer (♻️ reuse) ·
**03** Test Generator · **04** Standards Agent (♻️ reuse) · **05** Assemble Report.
Steps 6–7 below (`graph.py` wiring) are not a slide block — the teacher draws
them on the board.

| Step | Block | Where                | What to do                                                        | Time   |
|------|-------|----------------------|-------------------------------------------------------------------|--------|
| 1    | 01    | `agents/coordinator.py`     | **`route_pr`** — call `get_pr_diff` / `get_changed_files`, set `has_tests`, decide small/large route | 5 min  |
| 2    | 01    | `agents/coordinator.py`     | **`decide_route`** — return list of node names (parallel dispatch) | 2 min  |
| 3    | 03    | `agents/test_generator.py`  | **3 tools** — `get_existing_tests`, `get_source_functions`, `analyze_coverage` | 10 min |
| 4    | 03    | `agents/test_generator.py`  | **Agent** — `create_react_agent(llm, test_tools)` + `run_test_generator` | 5 min  |
| 5    | 02/04/05 | `graph.py`        | **Imports** ♻️ — `code_analyzer_subgraph` (Day 1, real subgraph), `run_standards_agent` (Day 2, agent-as-node), `run_test_generator` (your code, agent-as-node), `assemble_report` | 2 min  |
| 6    | board | `graph.py`           | **Add nodes** — coordinator + 3 agents + report (5 nodes total)   | 4 min  |
| 7    | board | `graph.py`           | **Edges** — `START → coordinator`, conditional fan-out, all agents → `report → END`, then `compile()` | 9 min  |

**Shared state** (pre-written in `state.py`):

```python
class PRState(TypedDict):
    pr_diff: str              # Coordinator fills
    files_changed: list[str]  # Coordinator fills
    has_tests: bool           # Coordinator fills
    code_issues: list[dict]   # Code Analyzer writes
    test_stubs: list[str]     # Test Generator writes
    standards_report: dict    # Standards Agent writes
    final_report: str         # Report Assembler writes
    messages: Annotated[list, add_messages]
```

## Testing Your Team

By default `run.py` imports from `solution_graph.py`. Once your `graph.py`
is done, switch the import:

```python
# in run.py
from graph import graph   # was: from solution_graph import graph
```

Then run:

```bash
uv run python practice_day3/run.py
```

### What a good output looks like

```
🔍 PR Review Team — analyzing repository...

============================================================
📋 FINAL PR REVIEW REPORT
============================================================
## PR Review Report

### Issues Found
- HIGH: Division bug in get_statistics (utils.py, line 27)

### Generated Tests
- def test_get_statistics_zero_tasks(): ...

### Standards Violations
- Missing error handling in utils.py

### Recommendations
- Fix division bug, add missing tests
```

## Bonus Challenges

1. **Streaming output** — use `graph.stream(...)` instead of `graph.invoke(...)`
   and print each agent's result as it lands. With parallel fan-out, the order
   you see results in reflects which agent finished first.
2. **GitHub integration** — replace `subprocess git diff` with the GitHub API:
   read a real PR by number, post the final report as a PR comment.
3. **HITL gate** — require human approval in `report` before "shipping" the
   review (reuse the pattern from Day 2 `option_c_hitl.py`).
4. **Slack notification** — post the final report to a Slack channel via
   webhook when the pipeline finishes.
5. **New agent** — add a 4th sub-agent (e.g. "Security Reviewer" that searches
   for SQL injection / hardcoded secrets) and wire it into the parallel
   fan-out (add to `decide_route`'s return list + an edge to `report`).
6. **Promote an agent-as-node to a subgraph** — convert `agents/test_generator.py`
   or `agents/standards_agent.py` from a wrapper function into a real `StateGraph`
   subgraph (like Code Analyzer). Give it its own state schema with at least
   one *internal* key the parent doesn't see, and check the nesting in
   LangSmith.

## Break & Fix Debugging Sprint (30 min)

After the core task, `debugging/` has 3 broken pipelines. Your job is to
read LangSmith traces to diagnose what's wrong and fix it.

**Prereq — make sure your `.env` has LangSmith configured:**

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2-...        # get one at https://smith.langchain.com
LANGCHAIN_PROJECT=beetroot-workshop
```

**Run your assigned scenario:**

```bash
uv run python practice_day3/debugging/scenario_a_missing_node.py
uv run python practice_day3/debugging/scenario_b_encoding_error.py
uv run python practice_day3/debugging/scenario_c_circular_loop.py
```

**Workflow:**

1. Run the script — see the crash or wrong output in terminal
2. Open <https://smith.langchain.com> → your project → find the run
3. Identify the broken span (red ❌ or unusually slow / repeated)
4. Open the scenario file, find the broken function (named `*_broken`
   or `*_looping`)
5. Fix it, re-run, confirm trace is clean

Don't read the source first — run, diagnose from trace, then patch.
See `TEACHER_NOTES.md` for hints if you're stuck.
