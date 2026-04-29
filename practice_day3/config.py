"""Shared configuration for Day 3 multi-agent system."""

from pathlib import Path

REPO_PATH = Path(__file__).parent.parent / "sample_repo"
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "practice_day2" / "knowledge_base"

# Default LLM for all agents in this workshop
LLM_MODEL = "gpt-4o-mini"
