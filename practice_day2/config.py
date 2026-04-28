"""Shared configuration for Day 2 agent."""

from pathlib import Path

REPO_PATH = Path(__file__).parent.parent / "sample_repo"
KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base"

# Default LLM for all agents in this workshop
LLM_MODEL = "gpt-4o-mini"
