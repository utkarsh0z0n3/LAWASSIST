import json
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_sections():

    with open("../data/ipc_sections.json") as f:
        sections = json.load(f)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    chunks = []

    for sec in sections:

        texts = splitter.split_text(sec["text"])

        for t in texts:
            chunks.append({
                "act": sec["act"],
                "section": sec["section"],
                "text": t
            })

    return chunks


if __name__ == "__main__":

    chunks = chunk_sections()

    with open("../data/ipc_chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)