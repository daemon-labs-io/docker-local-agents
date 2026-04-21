import sys
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.insert(0, str(Path(__file__).parent))
import workshop.src.config as config


def load_documents():
    documents = []
    for file_path in config.DATA_DIR.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(
                {
                    "id": file_path.stem,
                    "source": file_path.name,
                    "content": content,
                }
            )
    return documents


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc["content"])
        for i, split in enumerate(splits):
            chunks.append(
                {
                    "id": f"{doc['id']}-{i}",
                    "source": doc["source"],
                    "content": split,
                }
            )
    return chunks


def main():
    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    return chunks


if __name__ == "__main__":
    main()
