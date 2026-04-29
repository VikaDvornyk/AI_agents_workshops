"""
Shared State for the PR Review Team
=====================================

All agents read from and write to this shared state.
The Coordinator fills in pr_diff and files_changed,
then each agent adds its results.
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class PRState(TypedDict):
    # Input — filled by Coordinator
    pr_diff: str
    files_changed: list[str]
    has_tests: bool

    # Code Analyzer output
    code_issues: list[dict]

    # Test Generator output
    test_stubs: list[str]

    # Standards Agent output
    standards_report: dict

    # Final report
    final_report: str

    # Internal messages for agent communication
    messages: Annotated[list, add_messages]
