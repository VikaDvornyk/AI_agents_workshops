"""
Practice Day 1: Building a Coding Agent with LangGraph
=======================================================

Your task: wire up the agent graph.
Tools are in tools.py — implement them first, then come here.

Follow the TODOs below step by step.
"""

from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import all_tools

load_dotenv()


# ============================================================
# Step 1: Define the State (done for you)
# ============================================================

class State(TypedDict):
    messages: Annotated[list, add_messages]


# Step 2 = tools.py (you already did it).


# ============================================================
# Step 3: Set up the LLM and the chatbot node
# ============================================================

# TODO: Initialize the OpenAI chat model (use LLM_MODEL from config)
#       and bind the tools so the LLM knows which ones it can call.
# Hint: from config import LLM_MODEL
#       llm = ChatOpenAI(model=LLM_MODEL)


def chatbot(state: State):
    """The main LLM node. Takes current state, returns the AI response."""
    # TODO: Call the LLM on state["messages"] and return it in the shape
    #       {"messages": [...]} so LangGraph can merge it into state.
    pass


# ============================================================
# Step 4: Build the graph
# ============================================================

# TODO: Create a StateGraph over the State type.
# TODO: Add two nodes — "chatbot" and "tools" (ToolNode wraps all_tools).
# TODO: Wire the edges:
#         START    -> chatbot
#         chatbot  -> tools  (if LLM requested one) — use tools_condition
#                  -> END    (otherwise)
#         tools    -> chatbot


# ============================================================
# Step 5: Checkpointer — persistence between calls
# ============================================================

# TODO: Create a MemorySaver and compile the graph with checkpointer=<it>.
#
# When you invoke the graph, pass a config so the checkpointer knows which
# conversation this is:
#     config = {"configurable": {"thread_id": "1"}}
#     graph.invoke({"messages": [...]}, config=config)
