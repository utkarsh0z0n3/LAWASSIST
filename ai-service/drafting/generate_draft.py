import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import ollama

INDEX_FOLDER = Path("../data/index")

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en")

print("Loading FAISS index...")
index = faiss.read_index(str(INDEX_FOLDER / "law_index.faiss"))

with open(INDEX_FOLDER / "metadata.json") as f:
    metadata = json.load(f)


# -------------------------
# Retrieve relevant laws
# -------------------------

def search_law(query, k=5):

    query_embedding = model.encode([query])

    D, I = index.search(np.array(query_embedding), k)

    results = []

    for idx in I[0]:
        results.append(metadata[idx])

    return results


# -------------------------
# Draft generator
# -------------------------

def generate_draft(case_details):

    search_query = f"bail procedure {case_details['offence']} BNSS section bail"

    chunks = search_law(search_query)

    context = "\n\n".join(
        [f"{c['act']} Section {c['section']}:\n{c['text']}" for c in chunks]
    )

    prompt = f"""
You are an Indian legal drafting assistant.

Use ONLY the legal context provided below.

Do NOT reference CrPC or IPC unless they appear in the context.

LEGAL CONTEXT
{context}

CASE DETAILS
Client Name: {case_details['client_name']}
Court: {case_details['court']}
Offence: {case_details['offence']}
Facts: {case_details['facts']}

Draft a professional bail application using this format:

IN THE COURT OF {case_details['court']}

BAIL APPLICATION

IN THE MATTER OF:
State vs {case_details['client_name']}

MOST RESPECTFULLY SHOWETH:

1. Facts of the Case
2. Legal Grounds
3. Grounds for Bail

PRAYER

Wherefore it is respectfully prayed that this Hon'ble Court
may grant bail to the applicant.

Only use the law sections provided in the context.
"""
    
    response = ollama.chat(
        model="deepseek-r1",
        messages=[{"role": "user", "content": prompt}]
    )

    print("\n======= DRAFT =======\n")
    print(response["message"]["content"])
    print("\n=====================\n")


# -------------------------
# CLI input
# -------------------------

if __name__ == "__main__":

    case_details = {
        "client_name": input("Client name: "),
        "court": input("Court: "),
        "offence": input("Offence: "),
        "facts": input("Case facts: ")
    }

    generate_draft(case_details)