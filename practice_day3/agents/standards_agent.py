"""Standards Agent — reuses Day 2 RAG."""

import sys
from pathlib import Path

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langsmith import traceable

from config import LLM_MODEL
from lib.json_utils import parse_json_from_response
from lib.prompts import STANDARDS_AGENT_PROMPT

# Insert day1 first, then day2 — so day2 ends up in front on sys.path and
# `from solution_rag` resolves to day2.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "practice_day1"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "practice_day2"))

from solution_rag import search_knowledge_base
from solution_tools import get_file_content, search_codebase

standards_tools = [get_file_content, search_codebase, search_knowledge_base]
llm = ChatOpenAI(model=LLM_MODEL)
standards_agent = create_react_agent(llm, standards_tools)


@traceable(name="Standards Agent")
def run_standards_agent(state):
    """Check code against coding standards using RAG. Returns structured JSON."""
    files = state.get("files_changed", [])

    query = f"Review these files against our coding standards: {files}"

    result = standards_agent.invoke({
        "messages": [
            SystemMessage(content=STANDARDS_AGENT_PROMPT),
            {"role": "user", "content": query},
        ]
    })

    response = result["messages"][-1].content
    parsed = parse_json_from_response(response)

    if parsed:
        standards_report = parsed
    else:
        standards_report = {
            "violations": [{"description": response}],
            "recommendations": [],
            "pr_summary": response[:200],
        }

    return {
        "standards_report": standards_report,
        "messages": [{"role": "assistant", "content": f"[Standards Agent] Found {len(standards_report.get('violations', []))} violations"}],
    }
