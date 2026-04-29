"""Code Analyzer — Day 1 agent wrapped as a real LangGraph subgraph.

This is the *explicit subgraph* pattern: we build a `StateGraph` with its own
state schema, compile it, and let the parent graph call it as a node. Compare
with `solution_test_generator.py` / `standards_agent.py`, which use the
*agent-as-node* pattern (a wrapper function that invokes a ReAct agent).

Why a subgraph here:
  - The Day 1 agent has internal stages (build query → run ReAct → parse JSON)
    that benefit from being separate nodes — each shows up as its own span in
    LangSmith, which makes the debugging sprint easier.
  - `raw_response` is internal state: it's used between `analyze` and `parse`
    but never leaks into the parent `PRState`. That's the isolation benefit.
  - State mapping with the parent is automatic because shared keys
    (`pr_diff`, `files_changed`, `code_issues`, `messages`) match by name.
"""

import sys
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

from config import LLM_MODEL
from lib.json_utils import parse_json_from_response
from lib.prompts import CODE_ANALYZER_PROMPT

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "practice_day1"))

from solution_tools import all_tools as day1_tools


class CodeAnalyzerState(TypedDict):
    # Inputs — shared with parent PRState (LangGraph maps them by name)
    pr_diff: str
    files_changed: list[str]
    # Outputs — shared with parent PRState
    code_issues: list[dict]
    messages: Annotated[list, add_messages]
    # Internal — only this subgraph sees this field
    raw_response: str


llm = ChatOpenAI(model=LLM_MODEL)
_react_agent = create_react_agent(llm, day1_tools)


def analyze(state: CodeAnalyzerState) -> dict:
    """Run the Day 1 ReAct agent on the PR diff and stash its raw response."""
    query = (
        f"Analyze these files for bugs and issues: {state['files_changed']}. "
        f"Here is the diff:\n{state['pr_diff'][:2000]}"
    )
    result = _react_agent.invoke({
        "messages": [
            SystemMessage(content=CODE_ANALYZER_PROMPT),
            {"role": "user", "content": query},
        ]
    })
    return {"raw_response": result["messages"][-1].content}


def parse(state: CodeAnalyzerState) -> dict:
    """Extract structured issues from the agent's raw response."""
    response = state["raw_response"]
    parsed = parse_json_from_response(response)

    if parsed:
        code_issues = parsed.get("issues", [])
    else:
        code_issues = [{"description": response, "severity": "medium", "file": "unknown"}]

    return {
        "code_issues": code_issues,
        "messages": [{"role": "assistant", "content": f"[Code Analyzer] Found {len(code_issues)} issues"}],
    }


_builder = StateGraph(CodeAnalyzerState)
_builder.add_node("analyze", analyze)
_builder.add_node("parse", parse)
_builder.add_edge(START, "analyze")
_builder.add_edge("analyze", "parse")
_builder.add_edge("parse", END)

code_analyzer_subgraph = _builder.compile()
