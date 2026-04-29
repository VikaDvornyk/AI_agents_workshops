"""PR Review Team — Complete Multi-Agent Graph (SOLUTION)

True parallel fan-out: each agent is its own node. The Coordinator dispatches
to one or three agents based on PR size; LangGraph runs the dispatched nodes
concurrently and waits at `report` until all of them finish.
"""

from dotenv import load_dotenv
from langgraph.graph import START, END, StateGraph

from state import PRState
from agents.solution_coordinator import route_pr, decide_route
from agents.code_analyzer import code_analyzer_subgraph
from agents.solution_test_generator import run_test_generator
from agents.standards_agent import run_standards_agent
from report import assemble_report

load_dotenv()


# Build the multi-agent graph
graph_builder = StateGraph(PRState)

# Nodes — each agent is its own node, runs concurrently when dispatched.
# `code_analyzer` is a *compiled subgraph* (see code_analyzer.py) —
# LangGraph treats it as a nested graph and maps shared state keys
# (pr_diff, files_changed, code_issues, messages) automatically.
# The other two are *agent-as-node* wrappers: ReAct agents invoked from
# inside a regular function. Both patterns are valid; the README explains
# the trade-offs.
graph_builder.add_node("coordinator", route_pr)
graph_builder.add_node("code_analyzer", code_analyzer_subgraph)
graph_builder.add_node("test_generator", run_test_generator)
graph_builder.add_node("standards_agent", run_standards_agent)
graph_builder.add_node("report", assemble_report)

# Edges
graph_builder.add_edge(START, "coordinator")

# Coordinator dispatches based on PR size:
#   small → ["code_analyzer"]
#   large → ["code_analyzer", "test_generator", "standards_agent"]  (parallel)
graph_builder.add_conditional_edges("coordinator", decide_route)

# All agent paths converge at "report".
# LangGraph waits only for whichever nodes were actually scheduled.
graph_builder.add_edge("code_analyzer", "report")
graph_builder.add_edge("test_generator", "report")
graph_builder.add_edge("standards_agent", "report")
graph_builder.add_edge("report", END)

graph = graph_builder.compile()
