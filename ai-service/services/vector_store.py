# File: services/vector_store.py
import chromadb
from huggingface_hub import InferenceClient
from core.config import (
    EMBEDDING_MODEL,
    HF_API_KEY,
    CHROMA_API_KEY,
    CHROMA_TENANT,
    CHROMA_DATABASE,
)

# ✅ Hugging Face Inference Client instead of local model
hf_client = InferenceClient(
    model=EMBEDDING_MODEL,
    token=HF_API_KEY
)

client = chromadb.CloudClient(
    tenant=CHROMA_TENANT,
    database=CHROMA_DATABASE,
    api_key=CHROMA_API_KEY
)

collection = client.get_or_create_collection("modx_knowledge_base")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Get embeddings from Hugging Face Inference API."""
    embeddings = []
    for text in texts:
        result = hf_client.feature_extraction(text)
        embeddings.append(result[0] if isinstance(result[0], list) else result)
    return embeddings


def add_documents_to_store(documents_with_metadata):
    """Adds documents with their metadata to Chroma Cloud."""
    if not documents_with_metadata:
        return

    ids = [item[0] for item in documents_with_metadata]
    documents = [item[1] for item in documents_with_metadata]
    metadatas = [item[2] for item in documents_with_metadata]

    embeddings = embed_texts(documents)

    collection.upsert(
        embeddings=embeddings,
        documents=documents,
        ids=ids,
        metadatas=metadatas
    )
    print(f"✅ Successfully upserted {len(documents)} documents.")


def find_similar_document_ids(query_text: str, n_results=10) -> list[str]:
    """Finds the most semantically similar documents based on a query."""
    query_embedding = embed_texts([query_text])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where={"doc_type": "project"}
    )
    return results['ids'][0]


def delete_document_from_store(doc_id: str):
    """Deletes a document by its ID from ChromaDB."""
    try:
        collection.delete(ids=[doc_id])
        print(f"✅ Deleted document {doc_id} from ChromaDB")
    except Exception as e:
        print(f"❌ Error deleting document {doc_id}: {e}")
