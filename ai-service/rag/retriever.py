import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

_ROOT = Path(__file__).resolve().parent.parent
_INDEX_DIR = _ROOT / "data" / "index"

_model: SentenceTransformer | None = None
_index = None
_metadata: list | None = None


def _load_store():
    global _model, _index, _metadata
    if _model is not None:
        return
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    _index = faiss.read_index(str(_INDEX_DIR / "law_index.faiss"))
    with open(_INDEX_DIR / "metadata.json", encoding="utf-8") as f:
        _metadata = json.load(f)


def retrieve(query: str, k: int = 5):
    _load_store()
    q = _model.encode([query])
    D, I = _index.search(np.array(q), k)
    results = []
    for idx in I[0]:
        results.append(_metadata[idx])
    return results
