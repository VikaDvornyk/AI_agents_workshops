"""
Phase 3 — Option B: Shrink Cost
=================================

Reduce token usage and cost by:
1. Shortening the system prompt (remove 50%)
2. Reducing RAG chunk size (500 → 300 tokens)
3. Limiting conversation history (last 4 turns only)

Measure: % cost reduction vs baseline (check in LangSmith)
"""

import sys
from pathlib import Path
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# Insert day1 first, then day2 — so day2 ends up in front of day1 on sys.path.
# `config` exists in both days; day2's has KNOWLEDGE_BASE_PATH, day1's doesn't.
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "practice_day1"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import KNOWLEDGE_BASE_PATH, LLM_MODEL
from solution_tools import all_tools as day1_tools

load_dotenv()

# Smaller chunks = fewer tokens per retrieval
loader = DirectoryLoader(str(KNOWLEDGE_BASE_PATH), glob="*.md", loader_cls=TextLoader)
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(docs)
vectorstore = FAISS.from_documents(chunks, OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})  # k=2 instead of k=3


@tool
def search_knowledge_base(query: str) -> str:
    """Search coding standards. Returns relevant excerpts."""
    results = retriever.invoke(query)
    if not results:
        return "No relevant standards found."
    return "\n---\n".join([doc.page_content for doc in results])


combined_tools = day1_tools + [search_knowledge_base]

# Shorter system prompt — 50% reduction
SHORT_PROMPT = """You are a code reviewer. Use tools to read code and check standards.
Be concise. Reference file names and line numbers."""


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model=LLM_MODEL)
llm_with_tools = llm.bind_tools(combined_tools)


def chatbot(state: State):
    # Limit history to last 4 messages + system prompt
    msgs = state["messages"]
    if len(msgs) > 5:
        msgs = [msgs[0]] + msgs[-4:]
    return {"messages": [llm_with_tools.invoke(msgs)]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=combined_tools))
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph = graph_builder.compile()


def chat_lean():
    print("\nLean Agent (cost-optimized) — type your questions, 'quit' to exit\n")

    messages = [SystemMessage(content=SHORT_PROMPT)]

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
    chat_lean()
