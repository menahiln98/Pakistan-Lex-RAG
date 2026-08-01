import fitz  # PyMuPDF
import os

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

if __name__ == "__main__":
    folder = "data/raw_pdfs"
    files = os.listdir(folder)

    for filename in files:
        path = os.path.join(folder, filename)
        print(f"\n{'='*50}")
        print(f"FILE: {filename}")
        print('='*50)
        try:
            text = extract_text(path)
            print(f"Extracted {len(text)} characters")
            print("First 300 chars:")
            print(text[:300])
            if len(text.strip()) < 100:
                print("⚠️ WARNING: very little text extracted — might be a scanned PDF needing OCR")
        except Exception as e:
            print(f"❌ ERROR: {e}")