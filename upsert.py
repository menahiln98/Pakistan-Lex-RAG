import json
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("pakistan-rights-assistant")

if __name__ == "__main__":
    with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    vectors = []
    for chunk in chunks:
        vectors.append({
            "id": chunk["chunk_id"],
            "values": chunk["embedding"],
            "metadata": {
                "file_id": chunk["file_id"],
                "text": chunk["text"]
            }
        })

    # Pinecone recommends batching upserts (100 at a time)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted {i+len(batch)}/{len(vectors)}")

    print("Done.")