"""
Phase 1: Connect LangSmith & Record Baseline
==============================================

This runs the same agent as chat.py but with LangSmith tracing enabled.
Every LLM call, tool call, and decision is visible in the LangSmith dashboard.

Setup:
1. Create a free account at https://smith.langchain.com
2. Get your API key from Settings → API Keys
3. Set env vars below (or add to .env)
4. Run this script and open LangSmith dashboard to see traces

Baseline Metrics to Record:
- Average tokens per run
- Average cost per run
- Number of tool calls per query
- Error rate
- Latency (seconds)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage

load_dotenv()

# LangSmith config is in .env file:
#   LANGCHAIN_TRACING_V2=true
#   LANGCHAIN_API_KEY=lsv2-your-key-here
#   LANGCHAIN_PROJECT=ai-agents-workshop

from solution_agent import graph
from prompts import SYSTEM_PROMPT

# Baseline queries — run all of them, then check LangSmith dashboard
BASELINE_QUERIES = [
    "What does this project do?",
    "Find bugs in utils.py",
    "Review utils.py against our coding standards",
    "What do our testing guidelines say about coverage?",
]


def run_baseline():
    print("Running baseline queries with LangSmith tracing...\n")

    for i, query in enumerate(BASELINE_QUERIES, 1):
        print(f"[{i}/{len(BASELINE_QUERIES)}] {query}")
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            {"role": "user", "content": query},
        ]
        # Fresh thread per query — each baseline run is independent
        config = {"configurable": {"thread_id": f"baseline-{i}"}}
        try:
            result = graph.invoke({"messages": messages}, config=config)
            response = result["messages"][-1].content
            print(f"  Response: {response[:100]}...\n")
        except Exception as e:
            print(f"  Error: {e}\n")

    print("=" * 60)
    print("Now open https://smith.langchain.com to see your traces!")
    print("Record these metrics:")
    print("  - Average tokens per run")
    print("  - Average cost per run")
    print("  - Number of tool calls per query")
    print("  - Error rate")
    print("  - Latency (seconds)")
    print("=" * 60)


if __name__ == "__main__":
    run_baseline()
