from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "sample-docs"
EMBEDDING_MODEL = "nomic-embed-text"
GENERATION_MODEL = "qwen2.5:1.5b"
OLLAMA_BASE_URL = "http://ollama:11434"
CHROMA_HOST = "chromadb"
COLLECTION_NAME = "workshop-docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
