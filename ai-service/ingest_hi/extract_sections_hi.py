import re
import json
from pathlib import Path

CLEAN_FOLDER = Path("../data/clean_hi")
SECTION_FOLDER = Path("../data/sections_hi")

SECTION_FOLDER.mkdir(exist_ok=True)


def extract_sections(text, act_name):

    # Match patterns like:
    # ॥100
    # 100.
    # ॥ 100
    pattern = r"(॥\s*\d+|\n\d{1,3}\.)"

    parts = re.split(pattern, text)

    sections = []

    for i in range(1, len(parts), 2):

        header = parts[i]
        body = parts[i + 1]

        # Extract number
        match = re.search(r"\d+", header)
        if not match:
            continue

        section_number = match.group()

        clean_text = body.strip()

        # 🚫 Skip garbage sections
        if len(clean_text) < 30:
            continue

        sections.append({
            "act": act_name,
            "section": section_number,
            "text": clean_text,
            "language": "hi"
        })

    return sections


def process_all():

    for file in CLEAN_FOLDER.glob("*_clean.txt"):

        print("Processing", file.name)

        with open(file, encoding="utf-8") as f:
            text = f.read()

        act_name = file.stem.replace("_clean", "")

        sections = extract_sections(text, act_name)

        output_file = SECTION_FOLDER / file.name.replace("_clean.txt", "_sections.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    process_all()