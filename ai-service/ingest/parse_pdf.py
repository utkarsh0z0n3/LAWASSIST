import fitz

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    return full_text


if __name__ == "__main__":
    text = extract_text("../data/ipc.pdf")

    with open("../data/ipc_raw.txt", "w") as f:
        f.write(text)