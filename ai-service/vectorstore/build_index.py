import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


model = SentenceTransformer("BAAI/bge-small-en")


with open("../data/ipc_chunks.json") as f:
    chunks = json.load(f)


texts = [c["text"] for c in chunks]

embeddings = model.encode(texts)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(np.array(embeddings))

faiss.write_index(index, "ipc_index.faiss")


with open("metadata.json", "w") as f:
    json.dump(chunks, f)