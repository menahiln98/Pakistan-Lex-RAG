import fitz
import pytesseract
from PIL import Image
import io

# Point to your Tesseract install if it's not on PATH:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def ocr_extract(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        full_text += text
        print(f"  page {page_num+1} done")
    return full_text

if __name__ == "__main__":
    broken_files = ["hec_harassment_policy.pdf", "minorities_commission_act.pdf", "peca_2016.pdf"]
    for filename in broken_files:
        path = f"data/raw_pdfs/{filename}"
        print(f"\nOCR-ing {filename}...")
        text = ocr_extract(path)
        print(f"Extracted {len(text)} chars, first 300:")
        print(text[:300])