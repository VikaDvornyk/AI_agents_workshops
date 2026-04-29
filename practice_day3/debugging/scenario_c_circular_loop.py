"""
Scenario C: Circular Agent Dependency
==========================================

SYSTEM IS BROKEN — Find the bug, read the trace, fix it, submit the PR Report.

What we broke:
  Standards Agent is configured to call Code Analyzer for "more context" when
  standards violations are found. Code Analyzer calls Standards Agent for style
  context. Result: nested loops INSIDE each parallel branch (Python recursion,
  not LangGraph dispatch — which makes it harder to spot in the graph topology).

What you see in LangSmith:
  Fan-out from Coordinator → code_analyzer + standards_agent run concurrently,
  but each contains many nested calls forming a loop — 50+ nested spans
  alternating "code_analyzer" / "standards_agent" inside each branch.
  Token count grows exponentially · run killed by max_tokens limit after 120s.

How to fix it:
  1. Add call_depth counter to state: if depth > 3 → return best-effort result
  2. Remove bi-directional dependency: Standards Agent must NOT call Code Analyzer
  3. Add visited_nodes set: if (node_type, hash) already seen → LoopError
  4. Set global max_iterations on Coordinator
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph

# Make parent package importable before local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env BEFORE local imports — agent modules instantiate ChatOpenAI at import time
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from state import PRState
from agents.solution_coordinator import route_pr, decide_route
from agents.solution_test_generator import run_test_generator
from report import assemble_report

_call_count = 0
MAX_CALLS = 6


def run_code_analyzer_looping(state):
    """Code Analyzer that asks Standards Agent for 'style context'."""
    global _call_count
    _call_count += 1

    if _call_count > MAX_CALLS:
        raise RecursionError(f"Circular dependency: code_analyzer ↔ standards_agent looped {_call_count}× before bailout.")

    print(f"  Code Analyzer called (iteration {_call_count})...")

    run_standards_agent_looping(state)

    return {
        "code_issues": [
            {"description": f"Found issues (after {_call_count} iterations)", "severity": "medium"},
        ],
    }


def run_standards_agent_looping(state):
    """Standards Agent that asks Code Analyzer for 'more context'."""
    global _call_count
    _call_count += 1

    if _call_count > MAX_CALLS:
        raise RecursionError(f"Circular dependency: standards_agent ↔ code_analyzer looped {_call_count}× before bailout.")

    print(f"  Standards Agent called (iteration {_call_count})...")

    run_code_analyzer_looping(state)

    return {
        "standards_report": {
            "violations": [{"description": f"Standards check (after {_call_count} iterations)"}],
            "recommendations": [],
            "pr_summary": "Done",
        },
    }


# Parallel fan-out graph — both code_analyzer and standards_agent loop internally
graph_builder = StateGraph(PRState)
graph_builder.add_node("coordinator", route_pr)
graph_builder.add_node("code_analyzer", run_code_analyzer_looping)  # ← LOOPS
graph_builder.add_node("test_generator", run_test_generator)
graph_builder.add_node("standards_agent", run_standards_agent_looping)  # ← LOOPS
graph_builder.add_node("report", assemble_report)

graph_builder.add_edge(START, "coordinator")
graph_builder.add_conditional_edges("coordinator", decide_route)
graph_builder.add_edge("code_analyzer", "report")
graph_builder.add_edge("test_generator", "report")
graph_builder.add_edge("standards_agent", "report")
graph_builder.add_edge("report", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    print("Running Scenario C: Circular Agent Dependency...\n")
    _call_count = 0  # reset before invoke
    try:
        result = graph.invoke({
            "pr_diff": "", "files_changed": [], "has_tests": False,
            "code_issues": [], "test_stubs": [], "standards_report": {},
            "final_report": "", "messages": [],
        })
        print("=" * 60)
        print(result["final_report"])
        print(f"\nTotal agent calls: {_call_count}")
        print("→ Open LangSmith to see the trace.")
    except Exception as e:
        print(f"CRASH: {e}")
        print("→ Open LangSmith to see the trace.")
