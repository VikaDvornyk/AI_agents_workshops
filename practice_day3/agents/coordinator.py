"""
PR Coordinator — YOUR FILE
============================

The Coordinator is the supervisor. It does NOT review code.
It only:
1. Gets the PR diff and changed files
2. Decides which agents to call based on PR size
"""

import subprocess

from config import REPO_PATH


def get_pr_diff():
    """Get the diff of the latest commits in the repo.

    NOTE: This is a workshop simplification. In a real PR-review bot this would
    fetch an actual pull request, e.g.:
        subprocess.run(["gh", "pr", "diff", str(pr_number)], ...)
    where `pr_number` comes from a GitHub Action / webhook payload. We use
    `git diff HEAD~3 HEAD` here so the workshop runs without `gh` CLI or tokens.
    """
    result = subprocess.run(
        ["git", "diff", "HEAD~3", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_PATH.parent,
    )
    return result.stdout or "No diff found."


def get_changed_files():
    """Get list of files changed in the latest commits (sample_repo only).

    NOTE: Same workshop simplification as `get_pr_diff`. In production this would be:
        subprocess.run(["gh", "pr", "view", str(pr_number), "--json", "files"], ...)
    or a GitHub API call to `GET /repos/{owner}/{repo}/pulls/{number}/files`.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~3", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_PATH.parent,
    )
    all_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    # Filter to sample_repo files and make paths relative to sample_repo/
    repo_files = [f.replace("sample_repo/", "") for f in all_files if f.startswith("sample_repo/")]
    # If no sample_repo changes, return all source files as default
    if not repo_files:
        repo_files = [f.name for f in REPO_PATH.rglob("*.py")]
    return repo_files


def route_pr(state):
    """Coordinator: analyze PR scope and decide which agents to call.

    Steps:
      1. Get the diff and changed files (helpers above).
      2. Set has_tests if any filename contains "test".
      3. Return state with: pr_diff, files_changed, has_tests, route.

    Routing rules:
      - ≤3 files AND no test files → route = "small"
      - otherwise                  → route = "large"
    """
    pass


def decide_route(state):
    """Conditional edge: dispatch agents in parallel based on PR size.

    Return a LIST of node names — LangGraph dispatches them concurrently.
    The node names must match what graph.py registers via add_node().

      - "large" route → all 3 agent nodes
      - "small" route → only the code analyzer
    """
    pass
