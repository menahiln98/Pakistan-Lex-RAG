import fitz
import pytesseract
from PIL import Image
import io
import os
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Files that need OCR instead of direct text extraction
OCR_FILES = {"hec_harassment_policy.pdf", "minorities_commission_act.pdf", "peca_2016.pdf"}

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def ocr_extract(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        full_text += pytesseract.image_to_string(img)
    return full_text

def clean_text(text):
    text = re.sub(r'\n{2,}', '\n', text)              # collapse multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)                 # collapse multiple spaces
    text = re.sub(r'^\s*[^\w\s]{1,3}\s*$', '', text, flags=re.MULTILINE)  # strip lone junk-symbol lines
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = text.strip()
    return text

if __name__ == "__main__":
    raw_folder = "data/raw_pdfs"
    clean_folder = "data/clean_text"
    os.makedirs(clean_folder, exist_ok=True)

    for filename in os.listdir(raw_folder):
        path = os.path.join(raw_folder, filename)
        print(f"Processing {filename}...")

        if filename in OCR_FILES:
            raw_text = ocr_extract(path)
        else:
            raw_text = extract_text(path)

        cleaned = clean_text(raw_text)

        out_name = filename.replace(".pdf", ".txt")
        out_path = os.path.join(clean_folder, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        print(f"  saved {out_name} ({len(cleaned)} chars)")

    print("\nAll done.")