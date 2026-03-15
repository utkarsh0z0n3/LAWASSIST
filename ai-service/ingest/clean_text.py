from pathlib import Path
import re

RAW_FOLDER = Path("../data/raw")
CLEAN_FOLDER = Path("../data/clean")

CLEAN_FOLDER.mkdir(exist_ok=True)


def clean_text(text):

    text = re.sub(r"THE GAZETTE OF INDIA.*", "", text)

    text = re.sub(r"\n\s+\n", "\n\n", text)

    return text


def process_all():

    for file in RAW_FOLDER.glob("*_raw.txt"):

        with open(file) as f:
            text = f.read()

        cleaned = clean_text(text)

        out_file = CLEAN_FOLDER / file.name.replace("_raw", "_clean")

        with open(out_file, "w") as f:
            f.write(cleaned)


if __name__ == "__main__":

    process_all()