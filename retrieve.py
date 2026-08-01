import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("pakistan-rights-assistant")
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

def retrieve(query, top_k=5):
    # BGE models perform better when queries are prefixed like this
    prefixed_query = "Represent this sentence for searching relevant passages: " + query
    query_embedding = model.encode(prefixed_query).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return results["matches"]

if __name__ == "__main__":
    query = "My manager keeps making inappropriate comments at work. What can I legally do?"
    matches = retrieve(query)

    for match in matches:
        print(f"\nScore: {match['score']:.4f}")
        print(f"Source: {match['metadata']['file_id']}")
        print(f"Text: {match['metadata']['text'][:200]}...")