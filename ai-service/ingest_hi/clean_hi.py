import re
from pathlib import Path

INPUT_FOLDER = Path("../data/raw_hi")
OUTPUT_FOLDER = Path("../data/clean_hi")

OUTPUT_FOLDER.mkdir(exist_ok=True)


def clean_text(text):

    # 🔥 Remove Gazette headers (strong)
    text = re.sub(r".*राजपत्र.*\n", "", text)

    # 🔥 Remove "अनुभाग", "भाग", etc.
    text = re.sub(r"अनुभाग.*\n", "", text)
    text = re.sub(r"भाग.*\n", "", text)

    # 🔥 Remove page indicators
    text = re.sub(r"आग\s*\d+.*", "", text)

    # 🔥 Remove isolated junk lines (very short garbage)
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # remove very short junk lines
        if len(line) < 3:
            continue

        # remove lines with mostly symbols
        if re.fullmatch(r"[^\u0900-\u097F]+", line):
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 🔥 Remove weird characters but keep Hindi
    text = re.sub(r"[^\u0900-\u097F0-9\s\.\,\-\(\)]", "", text)

    # 🔥 Normalize spacing
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


for file in INPUT_FOLDER.glob("*_raw.txt"):

    print("Cleaning", file.name)

    with open(file, encoding="utf-8") as f:
        text = f.read()

    cleaned = clean_text(text)

    output_file = OUTPUT_FOLDER / file.name.replace("_raw.txt", "_clean.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned)