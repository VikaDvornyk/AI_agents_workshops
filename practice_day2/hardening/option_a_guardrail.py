"""
Phase 3 — Option A: Add Input Guardrail
=========================================

Block prompt injections by validating user input before it reaches the agent.
Simple approach: check for known injection patterns.

Measure: does it block the injections from Phase 2?
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

load_dotenv()

from solution_agent import graph
from prompts import SYSTEM_PROMPT

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?prior\s+instructions",
    r"reveal\s+your\s+(system\s+)?prompt",
    r"you\s+are\s+now\s+in\s+maintenance\s+mode",
    r"disregard\s+(all\s+)?(your\s+)?rules",
    r"override\s+(your\s+)?instructions",
    r"forget\s+(all\s+)?your\s+instructions",
]


def check_input(user_input: str) -> tuple[bool, str]:
    """Check user input for injection patterns.

    Returns:
        (is_safe, reason)
    """
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, f"Blocked: input matches injection pattern '{pattern}'"
    return True, "OK"


def chat_with_guardrail():
    print("\nAgent with Input Guardrail — type your questions, 'quit' to exit\n")

    config = {"configurable": {"thread_id": "guardrail-1"}}
    is_first_turn = True

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        # Guardrail check
        is_safe, reason = check_input(user_input)
        if not is_safe:
            print(f"\n{reason}\n")
            continue

        new_messages: list[BaseMessage] = []
        if is_first_turn:
            new_messages.append(SystemMessage(content=SYSTEM_PROMPT))
            is_first_turn = False
        new_messages.append(HumanMessage(content=user_input))

        try:
            result = graph.invoke({"messages": new_messages}, config=config)
            print(f"\nAgent: {result['messages'][-1].content}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    chat_with_guardrail()
