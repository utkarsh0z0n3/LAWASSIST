import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import ollama

# Paths
INDEX_FOLDER = Path("../data/index")

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en")

print("Loading FAISS index...")
index = faiss.read_index(str(INDEX_FOLDER / "law_index.faiss"))

with open(INDEX_FOLDER / "metadata.json") as f:
    metadata = json.load(f)


# -------------------------
# Vector Search
# -------------------------

def search_law(query, k=5):

    query_embedding = model.encode([query])

    distances, indices = index.search(np.array(query_embedding), k)

    results = []

    for idx in indices[0]:
        results.append(metadata[idx])

    return results


# -------------------------
# Build Context
# -------------------------

def build_context(chunks):

    context_blocks = []

    for c in chunks:

        block = f"""
Act: {c['act']}
Chapter: {c['chapter']}
Section: {c['section']}

{c['text']}
"""

        context_blocks.append(block)

    return "\n\n".join(context_blocks)


# -------------------------
# Ask the LLM
# -------------------------

def ask_law(question):

    print("\nSearching law database...\n")

    chunks = search_law(question)

    context = build_context(chunks)

    prompt = f"""
You are an AI legal assistant specializing in Indian law.

Use ONLY the legal context below to answer the question.

If the answer is not contained in the provided legal sections,
respond with:

"Answer not found in the retrieved legal sections."

Always cite the Act and Section number.

------------------------

LEGAL CONTEXT

{context}

------------------------

QUESTION

{question}

------------------------

Answer clearly with legal citations.
"""

    print("Generating answer...\n")

    response = ollama.chat(
        model="deepseek-r1",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"]

    print("\n========== LEGAL ANSWER ==========\n")
    print(answer)
    print("\n==================================\n")


# -------------------------
# CLI
# -------------------------

if __name__ == "__main__":

    print("\nIndian Law Assistant\n")

    question = input("Ask a legal question: ")

    ask_law(question)