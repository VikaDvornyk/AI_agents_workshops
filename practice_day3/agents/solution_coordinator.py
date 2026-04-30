"""PR Coordinator — supervisor that routes to sub-agents."""

import subprocess

from langsmith import traceable

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


@traceable(name="PR Coordinator")
def route_pr(state):
    """Coordinator: analyze PR scope and decide which agents to call.

    Rules:
    - Small PR (≤3 files, no test files) → Code Analyzer only
    - Large PR (>3 files or has test files) → all 3 agents
    """
    diff = get_pr_diff()
    files = get_changed_files()
    has_tests = any("test" in f.lower() for f in files)

    # Update state with PR info
    state_update = {
        "pr_diff": diff,
        "files_changed": files,
        "has_tests": has_tests,
    }

    # Routing decision
    if len(files) <= 3 and not has_tests:
        return {**state_update, "route": "small"}
    else:
        return {**state_update, "route": "large"}


def decide_route(state):
    """Conditional edge: returns list of agent nodes to dispatch in parallel.

    - Small PR → only Code Analyzer
    - Large PR → all 3 agents fan out concurrently
    """
    route = state.get("route", "small")
    if route == "large":
        return ["code_analyzer", "test_generator", "standards_agent"]
    return ["code_analyzer"]
