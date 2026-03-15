import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("BAAI/bge-small-en")

index = faiss.read_index("vectorstore/bns_index.faiss")

with open("vectorstore/metadata.json") as f:
    metadata = json.load(f)


def retrieve(query, k=5):

    q = model.encode([query])

    D, I = index.search(np.array(q), k)

    results = []

    for idx in I[0]:
        results.append(metadata[idx])

    return resultss