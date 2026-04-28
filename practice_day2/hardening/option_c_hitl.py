"""
Phase 3 — Option C: Add Human-in-the-Loop Gate
================================================

The agent must ask for human approval before risky actions.
Risky = any action that modifies files, runs commands, or accesses sensitive data.

In this demo, the agent pauses and asks for confirmation
before executing tool calls.

Measure: which actions triggered approval? Was it annoying or useful?
"""

import sys
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Insert day1 first, then day2 — so day2 ends up in front of day1 on sys.path.
# `prompts` exists in both days with different content; day2 must win.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "practice_day1"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import LLM_MODEL
from prompts import SYSTEM_PROMPT
from solution_rag import search_knowledge_base
from solution_tools import all_tools as day1_tools

load_dotenv()

combined_tools = day1_tools + [search_knowledge_base]

# Define risk levels for each tool
RISKY_TOOLS = {"get_git_diff"}  # Could expose sensitive changes
SAFE_TOOLS = {"get_file_content", "search_codebase", "search_knowledge_base"}


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model=LLM_MODEL)
llm_with_tools = llm.bind_tools(combined_tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def human_approval(state: State):
    """Check if the pending tool call needs human approval."""
    last_message = state["messages"][-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return state

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        if tool_name in RISKY_TOOLS:
            print(f"\nAgent wants to call: {tool_name}({tool_call['args']})")
            approval = input("   Approve? (y/n): ").strip().lower()
            if approval != "y":
                return {
                    "messages": [
                        ToolMessage(
                            content=f"Action '{tool_name}' was denied by the user.",
                            tool_call_id=tool_call["id"],
                        )
                    ]
                }

    return state


def route_after_approval(state: State):
    """Route: if last message is a denial, go back to chatbot. Otherwise, execute tools."""
    last_message = state["messages"][-1]
    if isinstance(last_message, ToolMessage) and "denied" in last_message.content:
        return "chatbot"
    # Check if there are tool calls
    second_last = state["messages"][-1]
    if hasattr(second_last, "tool_calls") and second_last.tool_calls:
        return "tools"
    return END


# Build graph with HITL gate
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("human_approval", human_approval)
graph_builder.add_node("tools", ToolNode(tools=combined_tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition, {"tools": "human_approval", END: END})
graph_builder.add_conditional_edges("human_approval", route_after_approval)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()


def chat_with_hitl():
    print("\nAgent with Human-in-the-Loop — type your questions, 'quit' to exit")
    print(f"   Risky tools (need approval): {RISKY_TOOLS}")
    print(f"   Safe tools (auto-approved): {SAFE_TOOLS}\n")

    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        messages.append({"role": "user", "content": user_input})

        try:
            result = graph.invoke({"messages": messages})
            messages = result["messages"]
            print(f"\nAgent: {messages[-1].content}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    chat_with_hitl()
