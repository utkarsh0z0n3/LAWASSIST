import json
import re
from pathlib import Path

SECTION_FOLDER = Path("../data/sections")
CHUNK_FOLDER = Path("../data/chunks")

CHUNK_FOLDER.mkdir(exist_ok=True)


def chunk_section(section):

    text = section["text"]

    clauses = re.split(r"\(\d+\)", text)

    chunks = []

    for i, clause in enumerate(clauses):

        clause = clause.strip()

        if len(clause) < 40:
            continue

        chunk = {
            "act": section["act"],
            "chapter": section["chapter"],
            "section": section["section"],
            "clause": i,
            "text": clause
        }

        chunks.append(chunk)

    return chunks


def process_all():

    for file in SECTION_FOLDER.glob("*sections.json"):

        with open(file) as f:
            sections = json.load(f)

        all_chunks = []

        for sec in sections:

            chunks = chunk_section(sec)

            all_chunks.extend(chunks)

        out_file = CHUNK_FOLDER / file.name.replace("sections", "chunks")

        with open(out_file, "w") as f:
            json.dump(all_chunks, f, indent=2)

        print("Saved", out_file)


if __name__ == "__main__":

    process_all()