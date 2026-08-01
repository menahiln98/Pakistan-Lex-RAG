import os
import time
from dotenv import load_dotenv
from groq import Groq
from retrieve import retrieve
from rerank import rerank
from monitor import log_query

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a legal information assistant covering Pakistani law on women's rights, student rights, employee rights, children's rights, minority rights, and defamation/cyberbullying protection.

You will be given a user's question and relevant excerpts retrieved from actual Pakistani legal documents (Acts, Ordinances, policies). Using ONLY the provided excerpts, answer in this exact structure:

Legal citation: [Name the Act/Ordinance and section number if visible in the excerpts]

Exact provision: [Quote the most relevant part of the retrieved text accurately]

What this means: [Explain in plain, simple language what this provision means]

Does your situation fit?: [Walk through the legal elements/requirements against what the user described. Do NOT give a definitive yes/no verdict — explain what would need to be true for this to apply, so the user can judge for themselves]

Recommended steps:
1. [practical first step]
2. [who to contact/file with]
3. [what to document]
4. [escalation path if needed]

Keep in mind: This is general legal information based on available documents, not a legal determination or substitute for professional legal advice. Consult a lawyer or the relevant authority for guidance specific to your situation.

Rules:
- Never invent legal information not present in the retrieved excerpts
- If the excerpts don't clearly answer the question, say so honestly rather than guessing
- Stay calm and procedural in tone — never dramatize or emotionally escalate
- Never assess the truth of an accusation (especially for blasphemy-adjacent or defamation cases) — only explain procedural/legal protections
"""

def generate_answer(query, top_k=10, final_k=5, print_stream=True):
    t0 = time.time()
    matches = retrieve(query, top_k=top_k)
    reranked = rerank(query, matches)[:final_k]
    retrieval_time = time.time() - t0

    context = "\n\n---\n\n".join(
        f"[Source: {item['file_id']}]\n{item['text']}"
        for item in reranked
    )

    user_message = f"""User question: {query}

Retrieved legal excerpts:
{context}

Answer following the required structure."""

    t1 = time.time()
    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        stream=True
    )

    full_answer = ""
    first_token_time = None

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            if first_token_time is None:
                first_token_time = time.time() - t1
            full_answer += delta
            if print_stream:
                print(delta, end="", flush=True)

    generation_time = time.time() - t1

    if print_stream:
        print()

    log_query(
        query=query,
        retrieval_time=retrieval_time,
        generation_time=generation_time,
        time_to_first_token=first_token_time,
        top_scores=[round(item['rerank_score'], 4) for item in reranked],
        file_id_sources=[item['file_id'] for item in reranked]
    )

    return full_answer


if __name__ == "__main__":
    query = "My manager keeps making inappropriate comments at work. What can I legally do?"
    generate_answer(query)