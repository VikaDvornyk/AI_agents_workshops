"""
Tools for the Coding Agent — SOLUTION
=======================================
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
    full_path = REPO_PATH / path
    if not full_path.exists():
        available = sorted(str(f.relative_to(REPO_PATH)) for f in REPO_PATH.rglob("*.py"))
        return f"Error: file '{path}' not found. Available files: {available}"
    return full_path.read_text(encoding="utf-8", errors="replace")


@tool
def search_codebase(query: str) -> str:
    """Search across the codebase for functions, classes, or patterns matching the query.
    Returns relevant file paths and matched lines.

    Args:
        query: Search term — a function name, class name, keyword, or pattern
    """
    matches = []
    for f in REPO_PATH.rglob("*"):
        if not f.is_file():
            continue
        try:
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if query in line:
                    matches.append(f"{f}:{i}:{line}")
        except OSError:
            continue
    if matches:
        return "\n".join(matches)
    return f"No matches found for '{query}'"


@tool
def get_git_diff(commit_a: str, commit_b: str) -> str:
    """Return the diff between two commits or branches.
    Useful for understanding what changed and why.

    Args:
        commit_a: First commit hash or branch name (e.g., "HEAD~3")
        commit_b: Second commit hash or branch name (e.g., "HEAD")
    """
    result = subprocess.run(
        ["git", "diff", commit_a, commit_b],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_PATH.parent,
    )
    if not result.stdout.strip():
        return "No differences found between the specified commits."
    return result.stdout


# All tools in a list — used by the agent
all_tools = [get_file_content, search_codebase, get_git_diff]
