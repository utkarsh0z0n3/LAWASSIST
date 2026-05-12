import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from pathlib import Path

INPUT_FOLDER = Path("../data/laws_hi")
OUTPUT_FOLDER = Path("../data/raw_hi")

OUTPUT_FOLDER.mkdir(exist_ok=True)

for pdf_file in INPUT_FOLDER.glob("*.pdf"):

    print("Processing", pdf_file.name)

    doc = fitz.open(pdf_file)
    full_text = ""

    for i, page in enumerate(doc):

        # convert page to image
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # OCR (Hindi)
        text = pytesseract.image_to_string(img, lang="hin")

        full_text += text + "\n"

    output_file = OUTPUT_FOLDER / (pdf_file.stem + "_raw.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_text)