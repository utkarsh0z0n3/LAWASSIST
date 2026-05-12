import os

from openai import OpenAI

from .retriever import retrieve

_base_url = os.getenv("OPENAI_BASE_URL")
_client_kwargs = {}
if _base_url:
    _client_kwargs["base_url"] = _base_url.strip()

client = OpenAI(**_client_kwargs)

_DEFAULT_MODEL = "gpt-4o-mini"


def ask(question: str) -> str:
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

    model = os.getenv("LAWASSIST_OPENAI_MODEL", _DEFAULT_MODEL).strip() or _DEFAULT_MODEL

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
