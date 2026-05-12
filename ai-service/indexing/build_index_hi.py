import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

SECTION_FOLDER = Path("../data/sections_hi")
INDEX_FOLDER = Path("../data/index_hi")

INDEX_FOLDER.mkdir(exist_ok=True)

print("Loading embedding model...")
model = SentenceTransformer("intfloat/multilingual-e5-base")

all_chunks = []

print("Loading section files...")

for file in SECTION_FOLDER.glob("*.json"):
    with open(file, encoding="utf-8") as f:
        data = json.load(f)
        all_chunks.extend(data)

print("Total sections:", len(all_chunks))

texts = [c["text"] for c in all_chunks]

print("Creating embeddings...")
embeddings = model.encode([f"passage: {t}" for t in texts])

dimension = len(embeddings[0])
index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

print("Saving index...")

faiss.write_index(index, str(INDEX_FOLDER / "law_index.faiss"))

with open(INDEX_FOLDER / "metadata.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print("✅ Hindi index built!")