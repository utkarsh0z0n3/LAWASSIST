import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


model = SentenceTransformer("BAAI/bge-small-en")


with open("../data/bns_chunks.json") as f:
    chunks = json.load(f)


texts = [c["text"] for c in chunks]

embeddings = model.encode(texts)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))


faiss.write_index(index, "bns_index.faiss")


with open("metadata.json", "w") as f:
    json.dump(chunks, f)

print("Vector index created")