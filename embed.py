import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-base-en-v1.5')

if __name__ == "__main__":
    with open("data/chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    texts = [chunk["text"] for chunk in chunks]

    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)

    print(f"Done. Embedding shape: {embeddings.shape}")

    # attach embeddings back to each chunk
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding.tolist()

    with open("data/chunks_with_embeddings.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f)

    print("Saved to data/chunks_with_embeddings.json")