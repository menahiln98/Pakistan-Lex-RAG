import os
import json
import shutil
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from process_all import extract_text, ocr_extract, clean_text, OCR_FILES
from chunking import chunk_text

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("pakistan-rights-assistant")
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

RAW_FOLDER = "data/raw_pdfs"
ARCHIVE_FOLDER = "data/archive_pdfs"
CLEAN_FOLDER = "data/clean_text"
STATUS_FILE = "data/document_status.json"

os.makedirs(ARCHIVE_FOLDER, exist_ok=True)


def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def embed_and_upsert(file_id, text):
    chunks = chunk_text(text)
    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        vectors.append({
            "id": f"{file_id}_{i}",
            "values": embedding,
            "metadata": {"file_id": file_id, "text": chunk}
        })

    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        index.upsert(vectors=vectors[i:i+batch_size])

    print(f"  upserted {len(vectors)} chunks for {file_id}")


def add_document(pdf_path, category=None):
    filename = os.path.basename(pdf_path)
    file_id = filename.replace(".pdf", "")

    dest_path = os.path.join(RAW_FOLDER, filename)
    if pdf_path != dest_path:
        shutil.copy(pdf_path, dest_path)

    print(f"Processing {filename}...")
    if filename in OCR_FILES:
        raw_text = ocr_extract(dest_path)
    else:
        raw_text = extract_text(dest_path)
    cleaned = clean_text(raw_text)

    clean_path = os.path.join(CLEAN_FOLDER, f"{file_id}.txt")
    with open(clean_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    embed_and_upsert(file_id, cleaned)

    status = load_status()
    status[file_id] = {"status": "active", "category": category or "uncategorized"}
    save_status(status)

    print(f"Added and activated: {file_id}")


def delete_document(file_id):
    status = load_status()
    if file_id not in status:
        print(f"No record of {file_id}. Nothing to delete.")
        return

    # Remove all vectors for this file from Pinecone
    index.delete(filter={"file_id": file_id})
    print(f"Deleted all vectors for {file_id} from Pinecone.")

    # Move the raw PDF to archive (not permanently erased)
    raw_path = os.path.join(RAW_FOLDER, f"{file_id}.pdf")
    archive_path = os.path.join(ARCHIVE_FOLDER, f"{file_id}.pdf")
    if os.path.exists(raw_path):
        shutil.move(raw_path, archive_path)
        print(f"Moved {file_id}.pdf to archive.")

    status[file_id]["status"] = "deleted"
    save_status(status)


def restore_document(file_id):
    status = load_status()
    if file_id not in status or status[file_id]["status"] != "deleted":
        print(f"{file_id} is not in a deleted state.")
        return

    archive_path = os.path.join(ARCHIVE_FOLDER, f"{file_id}.pdf")
    raw_path = os.path.join(RAW_FOLDER, f"{file_id}.pdf")
    if os.path.exists(archive_path):
        shutil.move(archive_path, raw_path)

    # Re-use the already-cleaned text instead of re-processing from scratch
    clean_path = os.path.join(CLEAN_FOLDER, f"{file_id}.txt")
    with open(clean_path, "r", encoding="utf-8") as f:
        cleaned = f.read()

    embed_and_upsert(file_id, cleaned)

    status[file_id]["status"] = "active"
    save_status(status)
    print(f"Restored: {file_id}")


def list_documents():
    status = load_status()
    for file_id, info in status.items():
        print(f"{file_id}: {info['status']} ({info['category']})")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python manage_documents.py [add|delete|restore|list] [args]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        add_document(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif command == "delete":
        delete_document(sys.argv[2])
    elif command == "restore":
        restore_document(sys.argv[2])
    elif command == "list":
        list_documents()
    else:
        print("Unknown command.")