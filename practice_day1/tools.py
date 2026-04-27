"""
Tools for the Coding Agent — YOUR FILE
========================================

Implement the 3 tools below. The agent (LLM) will decide
WHEN and HOW to call them based on the docstring.

Remember: the LLM never sees your code — only the function name,
docstring, and parameter types.
"""

import subprocess

from langchain_core.tools import tool

from config import REPO_PATH


@tool
def get_file_content(path: str) -> str:
    """Read a file from the repository. Returns the full file content as a string.

    Args:
        path: Relative path to the file within the repository (e.g., "app.py", "models.py")
    """
    # TODO: read the file at REPO_PATH / path and return its contents.
    #       Handle the case when the file doesn't exist — return an error
    #       message instead of letting it raise.
    pass


@tool
def search_codebase(query: str) -> str:
    """Search across the codebase for functions, classes, or patterns matching the query.
    Returns relevant file paths and matched lines.

    Args:
        query: Search term — a function name, class name, keyword, or pattern
    """
    # TODO: run `grep -rn {query} {REPO_PATH}` via subprocess and return the
    #       matches. If there are none, return a clear "no matches" message
    #       (otherwise the LLM will think the search failed).
    pass


@tool
def get_git_diff(commit_a: str, commit_b: str) -> str:
    """Return the diff between two commits or branches.
    Useful for understanding what changed and why.

    Args:
        commit_a: First commit hash or branch name (e.g., "HEAD~3")
        commit_b: Second commit hash or branch name (e.g., "HEAD")
    """
    # TODO: run `git diff {commit_a} {commit_b}` via subprocess.
    #       Watch the working directory — it must be inside the git repo.
    #       Return the diff output, or a "no differences" message if empty.
    pass


# All tools in a list — used by the agent
all_tools = [get_file_content, search_codebase, get_git_diff]
