# Pakistan Rights Assistant

A Retrieval-Augmented Generation (RAG) assistant delivering grounded legal information on women's, student's, employee's, children's, and religious minority rights in Pakistan — including protection against false accusations and defamation.

Built entirely from scratch (no LangChain), covering the full RAG pipeline: document ingestion, OCR fallback, chunking, embedding, vector retrieval, reranking, and grounded generation, with dynamic document management.

## Features

- **Grounded legal answers** — every response cites the specific law and section, quotes the exact statutory text, explains the legal elements involved, and outlines the formal complaint procedure
- **Six legal categories** — Women's Rights, Children's Rights, Students' Rights, Employees' Rights, Religious Minorities, and Defamation/Cyberbullying protection
- **Dynamic document management** — add or remove entire source documents at runtime; deletions are fully reversible via an archive system
- **Performance-aware retrieval** — semantic search (BGE embeddings) combined with cross-encoder reranking for improved relevance
- **Custom-styled interface** — Streamlit UI with injected CSS for a distinct visual identity

## Tech Stack

| Component | Technology |
|---|---|
| Embeddings | HuggingFace (`BAAI/bge-base-en-v1.5`) |
| Vector Database | Pinecone |
| Reranking | Cross-encoder (`ms-marco-MiniLM-L-6-v2`) |
| LLM | Groq API |
| App / UI | Streamlit |
| Deployment | Streamlit Community Cloud |

## Architecture

PDF documents → OCR/text extraction → cleaning → chunking
→ BGE embeddings → Pinecone vector store
→ query → semantic retrieval → cross-encoder reranking
→ Groq (structured legal answer generation) → Streamlit UI

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/menahiln98/Pakistan-Lex-RAG.git
cd Pakistan-Lex-RAG
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

**3. Set environment variables**

Create a `.env` file in the project root:

PINECONE_API_KEY=your_pinecone_key
GROQ_API_KEY=your_groq_key

**4. Run the app**
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Document Management (CLI)

```bash
python manage_documents.py list
python manage_documents.py delete <file_id>
python manage_documents.py restore <file_id>
python manage_documents.py add <path_to_pdf> <category>
```

## Deployment

Deployed on Streamlit Community Cloud, connected directly to this GitHub repository. Environment secrets (`PINECONE_API_KEY`, `GROQ_API_KEY`) are configured in the app's Settings on Streamlit Cloud.

## Disclaimer

This assistant provides general legal information grounded in Pakistani statutory and constitutional law. It does not constitute legal advice. For matters requiring formal legal action, consult a qualified advocate.