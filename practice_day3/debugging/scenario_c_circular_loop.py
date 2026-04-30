"""
Scenario C: Circular Agent Dependency
==========================================

SYSTEM IS BROKEN — Find the bug, read the trace, fix it, submit the PR Report.

What we broke:
  Standards Agent is configured to call Code Analyzer for "more context" when
  uncertain. Code Analyzer calls Standards Agent for style context. The
  conditional edges form a real LangGraph cycle:
      coordinator → code_analyzer → standards_agent → code_analyzer → ...
  The cycle never reaches `report`.

What you see in LangSmith:
  Each iteration is its own node span — alternating "code_analyzer" and
  "standards_agent" in the trace tree. The run aborts with
  GraphRecursionError after `recursion_limit` super-steps (set low here so
  we don't burn tokens). In production this would loop until max_tokens or
  a wall-clock limit fired.

How to fix it:
  1. Add call_depth counter to state: if depth > 3 → return best-effort result
  2. Remove bi-directional dependency: Standards Agent must NOT route back to Code Analyzer
  3. Add visited_nodes set: if (node, input_hash) already seen → LoopError
  4. Lower `recursion_limit` on graph.invoke(..., {"recursion_limit": N}) as a safety net

Debug Checklist:
  □ Open LangSmith trace
  □ Spot the alternating span pattern (same two nodes repeating)
  □ Identify the conditional edges that form the cycle
  □ Apply fix (break the cycle OR add a depth/visited guard)
  □ Re-run
  □ Confirm trace ends at `report` instead of crashing
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError
from langgraph.graph import START, END, StateGraph

# Make parent package importable before local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env BEFORE local imports — agent modules instantiate ChatOpenAI at import time
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from state import PRState
from agents.solution_coordinator import route_pr
from report import assemble_report

_iteration = 0


def run_code_analyzer_looping(state):
    """Code Analyzer that escalates to Standards Agent for 'style context'."""
    global _iteration
    _iteration += 1
    print(f"  Code Analyzer called (iteration {_iteration})...")
    return {
        "code_issues": [
            {"description": f"Found issues (iter {_iteration})", "severity": "medium"},
        ],
    }


def run_standards_agent_looping(state):
    """Standards Agent that escalates to Code Analyzer for 'more context'."""
    global _iteration
    _iteration += 1
    print(f"  Standards Agent called (iteration {_iteration})...")
    return {
        "standards_report": {
            "violations": [{"description": f"Style check (iter {_iteration})"}],
            "recommendations": [],
            "pr_summary": "Done",
        },
    }


def code_analyzer_route(_state):
    """Always escalate to Standards Agent — half of the bi-directional bug."""
    return "standards_agent"


def standards_agent_route(_state):
    """Always escalate back to Code Analyzer — the other half of the bug."""
    return "code_analyzer"


# Cycle graph: coordinator → code_analyzer ↔ standards_agent → (never reaches) report
graph_builder = StateGraph(PRState)
graph_builder.add_node("coordinator", route_pr)
graph_builder.add_node("code_analyzer", run_code_analyzer_looping)
graph_builder.add_node("standards_agent", run_standards_agent_looping)
graph_builder.add_node("report", assemble_report)

graph_builder.add_edge(START, "coordinator")
graph_builder.add_edge("coordinator", "code_analyzer")
graph_builder.add_conditional_edges(
    "code_analyzer",
    code_analyzer_route,
    ["standards_agent", "report"],
)
graph_builder.add_conditional_edges(
    "standards_agent",
    standards_agent_route,
    ["code_analyzer", "report"],
)
graph_builder.add_edge("report", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    print("Running Scenario C: Circular Agent Dependency...\n")
    try:
        result = graph.invoke(
            {
                "pr_diff": "", "files_changed": [], "has_tests": False,
                "code_issues": [], "test_stubs": [], "standards_report": {},
                "final_report": "", "messages": [],
            },
            {"recursion_limit": 8},
        )
        print("=" * 60)
        print(result["final_report"])
        print("→ Open LangSmith to see the trace.")
    except GraphRecursionError as e:
        print(f"\nCRASH: GraphRecursionError — {e}")
        print("→ Open LangSmith: alternating code_analyzer ↔ standards_agent spans, never reaching `report`.")
    except Exception as e:
        print(f"\nCRASH: {e}")
        print("→ Open LangSmith to see the trace.")
