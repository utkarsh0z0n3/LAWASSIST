import json
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

CHUNK_FOLDER = Path("../data/chunks")
INDEX_FOLDER = Path("../data/index")

INDEX_FOLDER.mkdir(exist_ok=True)

print("Loading embedding model...")

model = SentenceTransformer("intfloat/multilingual-e5-base")

all_chunks = []
texts = []

print("Loading chunk files...")

for file in CHUNK_FOLDER.glob("*chunks.json"):

    with open(file) as f:
        chunks = json.load(f)

    for chunk in chunks:

        text = chunk["text"]

        texts.append(text)
        all_chunks.append(chunk)

print("Creating embeddings...")

embeddings = model.encode([f"passage: {t}" for t in texts])

dimension = embeddings.shape[1]

print("Building FAISS index...")

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

faiss.write_index(index, str(INDEX_FOLDER / "law_index.faiss"))

with open(INDEX_FOLDER / "metadata.json", "w") as f:
    json.dump(all_chunks, f)

print("Index built successfully")