"""Shared configuration for the coding agent."""

from pathlib import Path

# Path to the repository we'll analyze
REPO_PATH = Path(__file__).parent.parent / "sample_repo"

# Default LLM for all agents in this workshop
LLM_MODEL = "gpt-4o-mini"
