from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query, matches):
    pairs = [[query, match['metadata']['text']] for match in matches]
    scores = reranker.predict(pairs)

    results = []
    for match, score in zip(matches, scores):
        results.append({
            "score": match['score'],
            "rerank_score": float(score),
            "file_id": match['metadata']['file_id'],
            "text": match['metadata']['text']
        })

    reranked = sorted(results, key=lambda x: x['rerank_score'], reverse=True)
    return reranked

if __name__ == "__main__":
    from retrieve import retrieve

    query = "My manager keeps making inappropriate comments at work. What can I legally do?"
    matches = retrieve(query, top_k=10)

    reranked = rerank(query, matches)

    for item in reranked[:5]:
        print(f"\nCosine score: {item['score']:.4f}")
        print(f"Rerank score: {item['rerank_score']:.4f}")
        print(f"Source: {item['file_id']}")
        print(f"Text: {item['text'][:200]}...")