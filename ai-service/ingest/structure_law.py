import re
import json

def split_sections(text):

    pattern = r"(Section\s+\d+[A-Za-z]*)"

    parts = re.split(pattern, text)

    sections = []

    for i in range(1, len(parts), 2):
        section_title = parts[i]
        section_text = parts[i+1]

        sections.append({
            "section": section_title.strip(),
            "text": section_text.strip()
        })

    return sections


if __name__ == "__main__":

    with open("../data/ipc_raw.txt") as f:
        text = f.read()

    sections = split_sections(text)

    with open("../data/ipc_sections.json", "w") as f:
        json.dump(sections, f, indent=2)