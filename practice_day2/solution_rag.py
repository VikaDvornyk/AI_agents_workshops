"""RAG Setup — SOLUTION"""

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import KNOWLEDGE_BASE_PATH

load_dotenv()

INDEX_PATH = KNOWLEDGE_BASE_PATH.parent / "faiss_index"
embeddings = OpenAIEmbeddings()

if INDEX_PATH.exists():
    # allow_dangerous_deserialization=True: FAISS uses pickle; we trust our own index file
    vectorstore = FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
else:
    loader = DirectoryLoader(
        str(KNOWLEDGE_BASE_PATH),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(INDEX_PATH))

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


@tool
def search_knowledge_base(query: str) -> str:
    """Search the coding standards knowledge base.
    Use this to find best practices, code review rules, and testing guidelines.

    Args:
        query: What to search for (e.g., "naming conventions", "error handling", "test coverage")
    """
    results = retriever.invoke(query)
    if not results:
        return "No relevant standards found."
    return "\n\n---\n\n".join([doc.page_content for doc in results])


# Quick test — run this file directly to verify RAG works
if __name__ == "__main__":
    print(f"Index path: {INDEX_PATH}")
    print(f"Vector store ready (cached: {INDEX_PATH.exists()})")
    print(f"\n--- Test search: 'error handling' ---\n")
    print(search_knowledge_base.invoke("error handling"))
