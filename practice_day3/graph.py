"""
PR Review Team — Multi-Agent Graph — YOUR FILE
================================================

Connect all agents into one graph with parallel fan-out:
1. Coordinator → decides route (small or large PR)
2. small PR → only Code Analyzer
3. large PR → Code Analyzer + Test Generator + Standards Agent in PARALLEL
4. All scheduled agents converge at Report
"""

from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph

from state import PRState
from agents.coordinator import route_pr, decide_route

# TODO: import the 4 nodes you'll wire into the graph:
#   - code_analyzer_subgraph  (from code_analyzer — Day 1 reuse, real subgraph)
#   - run_test_generator      (from test_generator — your code)
#   - run_standards_agent     (from standards_agent — Day 2 reuse)
#   - assemble_report         (from report)

load_dotenv()


# ============================================================
# Build the graph — parallel fan-out
# ============================================================

# TODO: build the graph.
#
# 1. Create a StateGraph over PRState.
#
# 2. Register 5 nodes — coordinator, the 3 agents, and report.
#    Node names MUST match what decide_route returns
#    ("code_analyzer", "test_generator", "standards_agent").
#
# 3. Wire edges:
#      START → coordinator
#      coordinator → conditional (decide_route — fan-out to 1 or 3 agents)
#      each agent  → report     (parallel branches converge here)
#      report      → END
#
# 4. Compile and assign to `graph` (run.py imports it by that name).
