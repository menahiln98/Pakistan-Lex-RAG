import os
import json

def chunk_text(text, chunk_size=800, overlap=50):
    # Split on newlines (paragraph/line-like breaks) first
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

if __name__ == "__main__":
    clean_folder = "data/clean_text"
    output_path = "data/chunks.json"

    all_chunks = []

    for filename in os.listdir(clean_folder):
        path = os.path.join(clean_folder, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        file_id = filename.replace(".txt", "")
        chunks = chunk_text(text)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "file_id": file_id,
                "chunk_id": f"{file_id}_{i}",
                "text": chunk
            })

        print(f"{filename}: {len(chunks)} chunks")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Saved to {output_path}")