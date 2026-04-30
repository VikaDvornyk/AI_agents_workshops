"""Test Generator Agent — generates test stubs for uncovered functions."""

import re

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langsmith import traceable

from config import LLM_MODEL, REPO_PATH
from lib.json_utils import parse_json_from_response
from lib.prompts import TEST_GENERATOR_PROMPT


@tool
def get_existing_tests(file_path: str) -> str:
    """Read the existing test file to see what's already tested.

    Args:
        file_path: Path to test file (e.g., "tests/test_app.py")
    """
    full_path = REPO_PATH / file_path
    if not full_path.exists():
        return f"Error: test file '{file_path}' not found."
    return full_path.read_text(encoding="utf-8", errors="replace")


@tool
def get_source_functions(file_path: str) -> str:
    """List all public functions in a source file with their signatures.

    Args:
        file_path: Path to source file (e.g., "utils.py", "app.py")
    """
    full_path = REPO_PATH / file_path
    if not full_path.exists():
        return f"Error: file '{file_path}' not found."

    content = full_path.read_text(encoding="utf-8", errors="replace")
    functions = re.findall(r"^(def \w+\(.*?\)).*:", content, re.MULTILINE)
    if not functions:
        return "No functions found."
    return "\n".join(functions)


@tool
def analyze_coverage(file_path: str) -> str:
    """Check which functions in a source file are tested and which are not.

    Args:
        file_path: Path to source file (e.g., "utils.py")
    """
    source_path = REPO_PATH / file_path
    test_path = REPO_PATH / "tests" / "test_app.py"

    if not source_path.exists():
        return f"Error: file '{file_path}' not found."
    if not test_path.exists():
        return "Error: test file not found."

    source = source_path.read_text(encoding="utf-8", errors="replace")
    tests = test_path.read_text(encoding="utf-8", errors="replace")

    functions = re.findall(r"^def (\w+)\(", source, re.MULTILINE)
    functions = [f for f in functions if not f.startswith("_")]

    tested = [f for f in functions if f in tests]
    not_tested = [f for f in functions if f not in tests]

    lines = [f"Coverage for {file_path}:"]
    for f in tested:
        lines.append(f"  ✅ {f} — tested")
    for f in not_tested:
        lines.append(f"  ❌ {f} — NOT tested")

    total = len(functions)
    covered = len(tested)
    pct = round(covered / total * 100) if total > 0 else 0
    lines.append(f"\nCoverage: {covered}/{total} ({pct}%)")

    return "\n".join(lines)


test_tools = [get_existing_tests, get_source_functions, analyze_coverage]
llm = ChatOpenAI(model=LLM_MODEL)
test_generator_agent = create_react_agent(llm, test_tools)


@traceable(name="Test Generator")
def run_test_generator(state):
    """Generate test stubs for uncovered functions."""
    files = state.get("files_changed", [])
    source_files = [f for f in files if not f.startswith("tests/")]

    query = f"Analyze coverage for these files: {source_files}. Generate test stubs for any untested functions."

    result = test_generator_agent.invoke({
        "messages": [
            SystemMessage(content=TEST_GENERATOR_PROMPT),
            {"role": "user", "content": query},
        ]
    })

    response = result["messages"][-1].content
    parsed = parse_json_from_response(response)

    if parsed:
        test_stubs = parsed.get("tests", [response])
    else:
        test_stubs = [response]

    return {
        "test_stubs": test_stubs,
        "messages": [{"role": "assistant", "content": f"[Test Generator] Generated {len(test_stubs)} test stubs"}],
    }
