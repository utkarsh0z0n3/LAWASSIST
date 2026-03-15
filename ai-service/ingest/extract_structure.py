import re
import json
from pathlib import Path

CLEAN_FOLDER = Path("../data/clean")
SECTION_FOLDER = Path("../data/sections")

SECTION_FOLDER.mkdir(exist_ok=True)

LAW_NAME_MAP = {
    "THE BHARATIYA NYAYA SANHITA 2023": "BNS 2023",
    "THE BHARATIYA NAGARIK SURAKSHA SANHITA 2023": "BNSS 2023",
    "THE BHARATIYA SAKSHYA ADHINIYAM 2023": "BSA 2023"
}


def remove_noise(text):

    text = re.sub(r"--- PAGE \d+ ---", "", text)
    text = re.sub(r"CG-DL.*", "", text)
    text = re.sub(r"सी\..*", "", text)
    text = re.sub(r"_{5,}", "", text)

    return text


def clean_section_text(text):

    # remove marginal headings
    text = re.sub(r"\n[A-Z][a-z]+\n[a-z]+\n[a-z]+\.", "", text)

    # remove page separators
    text = re.sub(r"_{3,}", "", text)

    # remove section references like "1 of 1871"
    text = re.sub(r"\d+\s+of\s+\d{4}", "", text)

    # remove bracket markers
    text = re.sub(r"Sec\.\s*\d+\]", "", text)

    # normalize spaces
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text.strip()

def extract_structure(text, act_name):

    text = remove_noise(text)

    chapters = re.split(r"(CHAPTER\s+[IVXLCDM]+)", text)

    sections_data = []

    current_chapter = ""

    for i in range(len(chapters)):

        chunk = chapters[i]

        if re.match(r"CHAPTER\s+[IVXLCDM]+", chunk):

            current_chapter = chunk.strip()
            continue

        body = chunk

        sections = re.split(r"\n\s*(\d+)\.\s", body)

        for j in range(1, len(sections), 2):

            section_number = sections[j]
            section_body = clean_section_text(sections[j + 1])

            sections_data.append({
                "act": act_name,
                "chapter": current_chapter,
                "section": section_number,
                "text": section_body
            })

    return sections_data


def process_all():

    for file in CLEAN_FOLDER.glob("*_clean.txt"):

        print("Processing", file.name)

        with open(file, encoding="utf-8") as f:
            text = f.read()

        act_name = file.stem.replace("_clean", "").replace(",", "")
        act_name = LAW_NAME_MAP.get(act_name, act_name)

        sections = extract_structure(text, act_name)

        output_file = SECTION_FOLDER / file.name.replace("_clean.txt", "_sections.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2)

        print("Saved", output_file)


if __name__ == "__main__":
    process_all()