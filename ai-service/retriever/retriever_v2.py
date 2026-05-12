import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

# Paths
EN_INDEX = Path("../data/index")
HI_INDEX = Path("../data/index_hi")

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en")

print("Loading English index...")
en_index = faiss.read_index(str(EN_INDEX / "law_index.faiss"))
with open(EN_INDEX / "metadata.json") as f:
    en_meta = json.load(f)

print("Loading Hindi index...")
hi_index = faiss.read_index(str(HI_INDEX / "law_index.faiss"))
with open(HI_INDEX / "metadata.json", encoding="utf-8") as f:
    hi_meta = json.load(f)


# -------------------------
# MAIN SEARCH FUNCTION
# -------------------------

def search_law(query, k=5):

    query_embedding = model.encode([query])

    # Search English
    en_D, en_I = en_index.search(np.array(query_embedding), k)

    # Search Hindi
    hi_D, hi_I = hi_index.search(np.array(query_embedding), k)

    results = []

    # Add English results
    for idx in en_I[0]:
        chunk = en_meta[idx].copy()
        chunk["source"] = "en"
        results.append(chunk)

    # Add Hindi results
    for idx in hi_I[0]:
        chunk = hi_meta[idx].copy()
        chunk["source"] = "hi"
        results.append(chunk)

    return results


# -------------------------
# DEBUG CLI (OPTIONAL)
# -------------------------

if __name__ == "__main__":

    query = input("Enter query: ")

    results = search_law(query)

    print("\nTop Results:\n")

    for r in results:

        print(f"[{r['source'].upper()}] {r['act']} | Section {r['section']}")
        print(r["text"][:300])
        print("\n---\n")