"""
Practice Day 1: Building a Coding Agent — SOLUTION
====================================================
"""

from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from config import LLM_MODEL
from solution_tools import all_tools

load_dotenv()


# Step 1: State
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Step 2 lives in solution_tools.py — tool implementations.


# Step 3: LLM + chatbot node
llm = ChatOpenAI(model=LLM_MODEL)
llm_with_tools = llm.bind_tools(all_tools)


def chatbot(state: State) -> dict:
    """The main LLM node."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Step 4: Build graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=all_tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# Step 5: Checkpointer — agent remembers conversation between calls
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
