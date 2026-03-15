import fitz
from pathlib import Path

LAW_FOLDER = Path("../data/laws")
OUTPUT_FOLDER = Path("../data/raw")

OUTPUT_FOLDER.mkdir(exist_ok=True)


def extract_pdf_text(pdf_path):

    doc = fitz.open(pdf_path)

    pages = []

    for i, page in enumerate(doc):

        text = page.get_text()

        pages.append({
            "page": i + 1,
            "text": text
        })

    return pages


def save_raw_text(pages, output_file):

    with open(output_file, "w") as f:

        for p in pages:

            f.write(f"\n\n--- PAGE {p['page']} ---\n")

            f.write(p["text"])


def process_all_pdfs():

    pdf_files = list(LAW_FOLDER.glob("*.pdf"))

    print(f"Found {len(pdf_files)} law files")

    for pdf in pdf_files:

        print(f"Processing {pdf.name}")

        pages = extract_pdf_text(pdf)

        output_file = OUTPUT_FOLDER / f"{pdf.stem}_raw.txt"

        save_raw_text(pages, output_file)


if __name__ == "__main__":

    process_all_pdfs()

    print("All PDFs parsed successfully")