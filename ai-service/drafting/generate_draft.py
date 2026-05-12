"""
CLI for bail drafting using the same deterministic template as the API.

Optional: append retrieved statute excerpts (lazy-loads FAISS on demand).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from drafting.bail_template import build_bail_draft, validate_bail_draft
from llm.input_handler import create_user_data
from rag.retriever import retrieve


def _law_appendix(offence: str, facts: str, k: int = 3) -> str:
    q = f"bail procedure {offence} BNSS bail {facts[:200]}"
    chunks = retrieve(q, k=k)
    lines = ["\n---\n", "Relevant excerpts (reference only; verify against current law):\n"]
    for c in chunks:
        lines.append(f"\n{c.get('act', '')} Section {c.get('section', '')}:\n{c.get('text', '')[:800]}\n")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bail draft (Indian court template, EN/HI)")
    parser.add_argument(
        "--with-law-excerpts",
        action="store_true",
        help="Append top-k retrieved statute snippets (loads embedding model + FAISS)",
    )
    args = parser.parse_args()

    data = create_user_data()
    text, lang = build_bail_draft(data)
    issues = validate_bail_draft(
        text,
        lang,
        expect_judicial_custody=data.in_judicial_custody,
    )
    if args.with_law_excerpts:
        text = text + _law_appendix(data.offence, data.facts)

    print(f"\nLanguage: {lang}\n")
    if issues:
        print("Checks:", ", ".join(issues))
    print("\n======= DRAFT =======\n")
    print(text)
    print("\n=====================\n")


if __name__ == "__main__":
    main()
