import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Using SentenceTransformerEmbeddingFunction which runs locally
# This is more reliable than the HF inference API for embeddings
hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)

collection = client.get_or_create_collection(
    name="memories",
    embedding_function=hf_ef
)

def add_memory_to_vector_store(memory_id: int, text: str, user_id: str):
    collection.add(
        documents=[text],
        ids=[str(memory_id)],
        metadatas=[{"user_id": user_id}]
    )

def search_memories(text: str, user_id: str, limit: int = 3):
    results = collection.query(
        query_texts=[text],
        n_results=limit,
        where={"user_id": user_id}
    )
    
    memories = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            memories.append({
                "id": int(results["ids"][0][i]),
                "text": results["documents"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else 1.0
            })
    return memories

def update_memory_in_vector_store(memory_id: int, text: str, user_id: str):
    collection.update(
        ids=[str(memory_id)],
        documents=[text],
        metadatas=[{"user_id": user_id}]
    )
