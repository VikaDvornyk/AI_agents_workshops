"""
Scenario A: Test Generator Disabled
========================================

SYSTEM IS BROKEN — Find the bug, read the trace, fix it, submit the PR Report.

What we broke:
  The test_generator node tries to import a module that doesn't exist.
  When Coordinator dispatches the parallel fan-out, test_generator crashes.
  Without error handling, the whole run aborts — even though code_analyzer
  and standards_agent may have completed in the other parallel branches.

What you see in LangSmith:
  Coordinator span → fan-out to 3 sibling spans →
  test_generator span ❌ ImportError: Module 'test_generator_v2' not found
  → entire run aborted (other branches' results are discarded).

How to fix it:
  1. Wrap the broken import in test_generator with try/except → return empty stubs
  2. OR: have decide_route exclude "test_generator" when the agent is unavailable
  3. Re-run → report generated without tests, with warning flag

Debug Checklist:
  □ Open LangSmith trace
  □ Find error span (red ❌)
  □ Read input that caused failure
  □ Identify fix category (timeout / encoding / loop / schema)
  □ Apply fix
  □ Re-run
  □ Confirm trace is clean
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph

# Make parent package importable before local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env BEFORE local imports — code_analyzer instantiates ChatOpenAI at import time
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from state import PRState
from agents.solution_coordinator import route_pr, decide_route
from agents.code_analyzer import code_analyzer_subgraph
from agents.standards_agent import run_standards_agent
from report import assemble_report


def run_test_generator_broken(state):
    raise ImportError("Module 'test_generator_v2' not found — agent was disabled in config")


# Parallel fan-out graph with the broken test_generator node
graph_builder = StateGraph(PRState)

graph_builder.add_node("coordinator", route_pr)
graph_builder.add_node("code_analyzer", code_analyzer_subgraph)
graph_builder.add_node("test_generator", run_test_generator_broken)  # ← BROKEN
graph_builder.add_node("standards_agent", run_standards_agent)
graph_builder.add_node("report", assemble_report)

graph_builder.add_edge(START, "coordinator")
graph_builder.add_conditional_edges("coordinator", decide_route)
graph_builder.add_edge("code_analyzer", "report")
graph_builder.add_edge("test_generator", "report")
graph_builder.add_edge("standards_agent", "report")
graph_builder.add_edge("report", END)

graph = graph_builder.compile()


if __name__ == "__main__":
    print("Running Scenario A: Test Generator Disabled...\n")
    try:
        result = graph.invoke({
            "pr_diff": "", "files_changed": [], "has_tests": False,
            "code_issues": [], "test_stubs": [], "standards_report": {},
            "final_report": "", "messages": [],
        })
        print(result["final_report"])
    except Exception as e:
        print(f"CRASH: {e}")
        print("\n→ Open LangSmith to see the trace.")
