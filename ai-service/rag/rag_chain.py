from .retriever import retrieve
from openai import OpenAI

client = OpenAI()


def ask(question):

    docs = retrieve(question)

    context = "\n\n".join([d["text"] for d in docs])

    prompt = f"""
You are an Indian legal assistant.

Use ONLY the provided legal context.

Context:
{context}

Question:
{question}

Cite sections.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content