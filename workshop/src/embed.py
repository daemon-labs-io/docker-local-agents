import sys
from pathlib import Path

import chromadb
import requests

sys.path.insert(0, str(Path(__file__).parent))
import workshop.src.config as config


def get_embedding(text: str) -> list[float]:
    response = requests.post(
        f"{config.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": config.EMBEDDING_MODEL, "prompt": text},
    )
    response.raise_for_status()
    return response.json()["embedding"]


def store_embeddings(chunks):
    client = chromadb.HttpClient(host=config.CHROMA_HOST, port=8000)

    try:
        client.delete_collection(name=config.COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=config.COLLECTION_NAME)

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [{"source": chunk["source"]} for chunk in chunks]

    print("Generating embeddings...")
    embeddings = [get_embedding(chunk["content"]) for chunk in chunks]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Stored {len(chunks)} embeddings in ChromaDB")


def main():
    from workshop.src.ingest import chunk_documents, load_documents

    print("Loading documents...")
    documents = load_documents()

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    store_embeddings(chunks)

    print("Done!")


if __name__ == "__main__":
    main()
