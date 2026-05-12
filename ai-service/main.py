"""FastAPI app: RAG Q&A and deterministic bail drafting."""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Repo root (parent of ai-service) for shared .env
_REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_REPO_ROOT / ".env")

# Ensure ai-service root is on path when launched from elsewhere
_svc_root = Path(__file__).resolve().parent
if str(_svc_root) not in sys.path:
    sys.path.insert(0, str(_svc_root))

from fastapi import FastAPI

from drafting.bail_template import build_bail_draft, validate_bail_draft
from drafting.schemas import BailDraftInput

app = FastAPI(title="LAWASSIST AI Service")


class AskBody(BaseModel):
    q: str = Field(..., min_length=1, description="Legal question for RAG")


@app.get("/")
def health():
    return {"status": "ok", "service": "lawassist-ai"}


@app.post("/ask")
def query(body: AskBody):
    from rag import ask as rag_ask

    return {"answer": rag_ask(body.q)}


@app.post("/draft/bail")
def draft_bail(body: BailDraftInput):
    text, lang = build_bail_draft(body)
    issues = validate_bail_draft(
        text,
        lang,
        expect_judicial_custody=body.in_judicial_custody,
    )
    return {"draft": text, "language": lang, "issues": issues}
