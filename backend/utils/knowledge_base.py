"""
utils/knowledge_base.py
Retrieval-Augmented Generation (RAG) using ChromaDB.
Add medical guidelines and retrieve relevant context.
"""
import chromadb
from chromadb.utils import embedding_functions
from utils.config import GEMINI_KEY  # if using Gemini embeddings

# Initialize ChromaDB client (persistent storage)
client = chromadb.PersistentClient(path="./chroma_db")

# Choose embedding function: either Gemini or sentence-transformers
# Using sentence-transformers as fallback (no API key needed)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
# If you have Gemini API key, you can use:
# embedding_fn = embedding_functions.GooglePalmEmbeddingFunction(api_key=GEMINI_KEY)

collection = client.get_or_create_collection(
    name="medical_guidelines",
    embedding_function=embedding_fn,
)

def add_documents(docs: list[str], metadatas: list[dict] = None):
    """
    Add documents to the vector store.
    Args:
        docs: list of document texts
        metadatas: optional list of metadata dicts
    """
    ids = [f"doc_{i}" for i in range(len(docs))]
    collection.add(documents=docs, metadatas=metadatas, ids=ids)

def retrieve_relevant(query: str, k: int = 3) -> list[str]:
    """
    Retrieve top-k relevant documents for the query.
    Returns list of document texts.
    """
    results = collection.query(query_texts=[query], n_results=k)
    # results['documents'] is a list of lists
    return results['documents'][0] if results['documents'] else []

# Example usage in tools:
# context = retrieve_relevant(en)
# if context:
#     prompt = f"Relevant medical guidelines:\n{context}\n\nPatient query: {en}\n..."