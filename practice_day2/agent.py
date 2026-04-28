"""
Practice Day 2: Extending the Agent with RAG
==============================================

Your task: add a RAG knowledge base to the Day 1 agent.
1. First set up RAG in rag.py (load docs, embed, create search tool)
2. Then wire everything together here

Follow the TODOs below.
"""

import sys
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Import your RAG tool (must be before Day 1 import)
from rag import search_knowledge_base

# Import Day 1 tools
sys.path.insert(0, str(Path(__file__).parent.parent / "practice_day1"))
from solution_tools import all_tools as day1_tools

load_dotenv()


# ============================================================
# Step 1: Combine Day 1 tools + RAG tool
# ============================================================

# TODO: Merge Day 1 tools with the RAG tool into one list
# combined_tools = day1_tools + [search_knowledge_base]


# ============================================================
# Step 2: State (same as Day 1)
# ============================================================

class State(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================================
# Step 3: Set up the LLM with ALL tools
# ============================================================

# TODO: Initialize the LLM and bind the combined tools
# Hint: from config import LLM_MODEL
#       llm = ChatOpenAI(model=LLM_MODEL)
#       llm_with_tools = llm.bind_tools(combined_tools)


# ============================================================
# Step 4: Build the graph (same pattern as Day 1)
# ============================================================

def chatbot(state: State):
    """The main LLM node."""
    # TODO: return {"messages": [llm_with_tools.invoke(state["messages"])]}
    pass


# TODO: Build the graph — same as Day 1 but with combined_tools
# graph_builder = StateGraph(State)
# graph_builder.add_node("chatbot", chatbot)
# graph_builder.add_node("tools", ToolNode(tools=combined_tools))
# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_conditional_edges("chatbot", tools_condition)
# graph_builder.add_edge("tools", "chatbot")


# ============================================================
# Step 5: Checkpointer (same as Day 1)
# ============================================================

# TODO: Create a MemorySaver and compile the graph with checkpointer=<it>.
#       chat.py already passes config={"configurable": {"thread_id": "1"}}.
# memory = MemorySaver()
# graph = graph_builder.compile(checkpointer=memory)
