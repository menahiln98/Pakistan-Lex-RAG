from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from generate import generate_answer
from manage_documents import add_document, delete_document, restore_document, list_documents, load_status

app = FastAPI(title="Pakistan Rights Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual frontend domain once deployed
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_TEMP = "data/uploads_temp"
os.makedirs(UPLOAD_TEMP, exist_ok=True)


@app.get("/")
def root():
    return {"status": "Pakistan Rights Assistant API is running"}


@app.post("/query")
def query_endpoint(question: str = Form(...)):
    answer = generate_answer(question, print_stream=False)
    return {"question": question, "answer": answer}


@app.get("/documents")
def documents_endpoint():
    return load_status()


@app.post("/documents/upload")
def upload_endpoint(file: UploadFile = File(...), category: str = Form(...)):
    temp_path = os.path.join(UPLOAD_TEMP, file.filename)
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    add_document(temp_path, category)

    os.remove(temp_path)

    return {"status": "added", "filename": file.filename, "category": category}


@app.delete("/documents/{file_id}")
def delete_endpoint(file_id: str):
    delete_document(file_id)
    return {"status": "deleted", "file_id": file_id}


@app.post("/documents/{file_id}/restore")
def restore_endpoint(file_id: str):
    restore_document(file_id)
    return {"status": "restored", "file_id": file_id}