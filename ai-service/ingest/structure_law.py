import re
import json


def detect_chapters(text):

    chapters = re.split(r"(CHAPTER\s+[IVXLCDM]+)", text)

    structured = []

    for i in range(1, len(chapters), 2):

        chapter_title = chapters[i]
        chapter_body = chapters[i + 1]

        structured.append({
            "chapter": chapter_title.strip(),
            "text": chapter_body
        })

    return structured


def detect_sections(chapters):

    sections = []

    for ch in chapters:

        parts = re.split(r"\n\s*(\d+)\.", ch["text"])

        for i in range(1, len(parts), 2):

            sec_num = parts[i]
            sec_body = parts[i + 1]

            sections.append({
                "chapter": ch["chapter"],
                "section": sec_num,
                "text": sec_body.strip()
            })

    return sections


if __name__ == "__main__":

    with open("../data/bns_clean.txt") as f:
        text = f.read()

    chapters = detect_chapters(text)

    sections = detect_sections(chapters)

    with open("../data/bns_sections.json", "w") as f:
        json.dump(sections, f, indent=2)

    print("Structure extraction complete")