"""
Test Generator Agent — YOUR FILE
==================================

This agent analyzes code coverage and generates test stubs
for functions that are not yet tested.
"""

import re

from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import LLM_MODEL, REPO_PATH
from lib.prompts import TEST_GENERATOR_PROMPT


@tool
def get_existing_tests(file_path: str) -> str:
    """Read the existing test file to see what's already tested.

    Args:
        file_path: Path to test file (e.g., "tests/test_app.py")
    """
    # TODO: read the file under REPO_PATH and return its content as a string
    pass


@tool
def get_source_functions(file_path: str) -> str:
    """List all public functions in a source file with their signatures.

    Args:
        file_path: Path to source file (e.g., "utils.py", "app.py")
    """
    # TODO: read the file, extract function definitions with a regex on `def NAME(...)`,
    # return them joined by newlines
    pass


@tool
def analyze_coverage(file_path: str) -> str:
    """Check which functions in a source file are tested and which are not.

    Args:
        file_path: Path to source file (e.g., "utils.py")
    """
    # TODO: read both source and test file, extract function names from source,
    # split into "tested" (name appears in test file) vs "not tested",
    # return a human-readable summary
    pass


# TODO: build the agent — make a tools list of the 3 @tool functions above,
# create a ChatOpenAI(model=LLM_MODEL), and wrap with create_react_agent(llm, tools)


def run_test_generator(state):
    """Generate test stubs for uncovered functions."""
    # TODO: invoke the agent with TEST_GENERATOR_PROMPT as system message
    # and a user query asking it to analyze coverage for state["files_changed"]
    # (skip files starting with "tests/"). Return {"test_stubs": [...]}.
    pass
