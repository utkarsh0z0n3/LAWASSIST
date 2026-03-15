import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import sys

INDEX_FOLDER = Path("../data/index")

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en")

print("Loading FAISS index...")
index = faiss.read_index(str(INDEX_FOLDER / "law_index.faiss"))

with open(INDEX_FOLDER / "metadata.json") as f:
    metadata = json.load(f)


def search(query, k=5):

    query_embedding = model.encode([query])

    D, I = index.search(np.array(query_embedding), k)

    results = []

    for idx in I[0]:

        results.append(metadata[idx])

    return results


if __name__ == "__main__":

    query = " ".join(sys.argv[1:])

    results = search(query)

    print("\nTop Results:\n")

    for r in results:

        print(f"{r['act']} | {r['chapter']} | Section {r['section']}")
        print(r["text"][:500])
        print("\n---\n")