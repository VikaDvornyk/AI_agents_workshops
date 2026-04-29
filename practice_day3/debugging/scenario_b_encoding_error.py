"""
Scenario B: Encoding Error in File
=======================================

SYSTEM IS BROKEN — Find the bug, read the trace, fix it, submit the PR Report.

What we broke:
  One file in the mock repo has a Latin-1 encoding (not UTF-8).
  Code Analyzer calls get_file_content → UnicodeDecodeError → returns garbage string.

What you see in LangSmith:
  Fan-out from Coordinator → 3 sibling spans →
  code_analyzer span → get_file_content tool call →
  retries 3× with same input · timeout after 30s.
  Other agents (test_generator, standards_agent) finish normally in parallel.

How to fix it:
  1. Fix get_file_content to try UTF-8 first, fallback to latin-1: errors="replace"
  2. Add encoding detection (chardet library)
  3. Code Analyzer should check for error keys before processing
"""

import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import create_react_agent

# Make parent package importable before local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load env BEFORE local imports — agent modules instantiate ChatOpenAI at import time
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from state import PRState
from config import LLM_MODEL, REPO_PATH
from agents.solution_coordinator import route_pr, decide_route
from agents.solution_test_generator import run_test_generator
from agents.standards_agent import run_standards_agent
from report import assemble_report

# Create a file with bad encoding
BAD_FILE = REPO_PATH / "legacy_module.py"


def setup_bad_file():
    """Create a file with Latin-1 encoding that breaks UTF-8 reading."""
    content = "# Legacy module\ndef calculate_résumé(data):\n    return data.encode('latin-1')\n"
    BAD_FILE.write_bytes(content.encode("latin-1"))


def cleanup_bad_file():
    if BAD_FILE.exists():
        BAD_FILE.unlink()


@tool
def get_file_content_broken(path: str) -> str:
    """Read a file from the repository."""
    full_path = REPO_PATH / path
    if not full_path.exists():
        return f"Error: file '{path}' not found."
    return full_path.read_text(encoding="utf-8")


@tool
def search_codebase(query: str) -> str:
    """Search the codebase."""
    result = subprocess.run(["grep", "-rn", query, str(REPO_PATH)], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else f"No matches for '{query}'"


def run_code_analyzer_broken(state):
    """BROKEN Code Analyzer — doesn't handle non-UTF-8 files."""
    tools = [get_file_content_broken, search_codebase]
    llm = ChatOpenAI(model=LLM_MODEL)
    agent = create_react_agent(llm, tools)

    files = state.get("files_changed", [])
    query = f"Analyze ALL files for bugs including legacy_module.py: {files + ['legacy_module.py']}"

    try:
        result = agent.invoke({
            "messages": [
                SystemMessage(content="You are a code analyzer. Read ALL files including legacy_module.py."),
                {"role": "user", "content": query},
            ]
        })
        response = result["messages"][-1].content
        return {"code_issues": [{"description": response, "severity": "medium"}]}
    except Exception as e:
        return {"code_issues": [{"description": f"AGENT CRASHED: {e}", "severity": "critical"}]}


# Parallel fan-out graph with broken code_analyzer
graph_builder = StateGraph(PRState)
graph_builder.add_node("coordinator", route_pr)
graph_builder.add_node("code_analyzer", run_code_analyzer_broken)  # ← BROKEN
graph_builder.add_node("test_generator", run_test_generator)
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
    print("Running Scenario B: Encoding Error...\n")
    setup_bad_file()
    try:
        result = graph.invoke({
            "pr_diff": "", "files_changed": [], "has_tests": False,
            "code_issues": [], "test_stubs": [], "standards_report": {},
            "final_report": "", "messages": [],
        })
        print("=" * 60)
        print(result["final_report"])
    except Exception as e:
        print(f"CRASH: {e}")
        print("\n→ Open LangSmith to see the trace.")
    finally:
        cleanup_bad_file()
