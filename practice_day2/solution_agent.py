"""Practice Day 2: Extending the Agent with RAG — SOLUTION"""

import sys
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from config import LLM_MODEL

# Import RAG tool (must be before Day 1 import to use local config)
from solution_rag import search_knowledge_base

# Import Day 1 tools
sys.path.insert(0, str(Path(__file__).parent.parent / "practice_day1"))
from solution_tools import all_tools as day1_tools

load_dotenv()

# Step 1: Combine all tools
combined_tools = day1_tools + [search_knowledge_base]


# Step 2: State
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Step 3: LLM + tools
llm = ChatOpenAI(model=LLM_MODEL)
llm_with_tools = llm.bind_tools(combined_tools)


# Step 4: Graph
def chatbot(state: State):
    """The main LLM node."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=combined_tools))

graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")

# Checkpointer — same pattern as Day 1 (conversation persists between calls)
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
