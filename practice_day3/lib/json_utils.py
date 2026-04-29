"""Shared helpers for parsing structured output from LLM agents."""

import json


def parse_json_from_response(text):
    """Extract JSON from LLM response (handles markdown code blocks)."""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
