"""
RAG Setup — YOUR FILE
======================

Set up a vector store knowledge base from coding standards documents.

Steps:
1. Load documents from knowledge_base/ folder
2. Split them into chunks
3. Create embeddings and store in a vector database
4. Create a retriever tool for the agent
"""

from langchain_core.tools import tool

from config import KNOWLEDGE_BASE_PATH


# ============================================================
# Step 1: Load documents
# ============================================================

# TODO: Load all .md files from KNOWLEDGE_BASE_PATH into a list of documents.
#       Use DirectoryLoader + TextLoader from langchain_community.document_loaders.
#       Glob pattern should match markdown files only.
#       Pass loader_kwargs={"encoding": "utf-8"} to DirectoryLoader so it
#       works on Windows (default codepage is cp1251/cp1252, not UTF-8).
#       Assign the result to a variable named `docs` — you'll use it in Step 2.


# ============================================================
# Step 2: Split into chunks
# ============================================================

# TODO: Split `docs` into smaller chunks for better retrieval.
#       Use RecursiveCharacterTextSplitter from langchain_text_splitters.
#       Experiment with chunk_size (300–800) and overlap (~10% of chunk_size).
#       Call .split_documents(docs) to get the list. Assign to `chunks`.


# ============================================================
# Step 3: Create vector store
# ============================================================

# TODO: Embed `chunks` and store them in an in-memory vector DB.
#       Use FAISS (from langchain_community.vectorstores) + OpenAIEmbeddings
#       (from langchain_openai). FAISS.from_documents(...) builds the store.
#       Then expose a retriever via .as_retriever(search_kwargs={"k": <n>}).
#       k = how many chunks to return per query. Start with 3.
#       Assign the retriever to `retriever` — Step 4 uses it.


# ============================================================
# Step 4: Create RAG tool
# ============================================================

@tool
def search_knowledge_base(query: str) -> str:
    """Search the coding standards knowledge base.
    Use this to find best practices, code review rules, and testing guidelines.

    Args:
        query: What to search for (e.g., "naming conventions", "error handling", "test coverage")
    """
    # TODO: Call retriever.invoke(query) to get the top-k chunks.
    #       Each chunk is a Document with a .page_content field.
    #       Join the page_content of all results into one readable string
    #       (a separator like "\n\n---\n\n" works well).
    pass


# ============================================================
# Step 5: Test it!
# ============================================================
# Run this file directly to check that RAG works:
#   uv run python rag.py
#
# Uncomment the block below once Steps 1–4 are done.
#
# if __name__ == "__main__":
#     print(f"Loaded {len(docs)} documents")
#     print(f"Split into {len(chunks)} chunks")
#     print(f"Vector store ready")
#     print(f"\n--- Test search: 'error handling' ---\n")
#     print(search_knowledge_base.invoke("error handling"))
