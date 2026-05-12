"""
CLI entrypoint for deterministic bail drafting (Indian court format, EN/HI).
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from drafting.bail_template import build_bail_draft, validate_bail_draft
from llm.input_handler import create_user_data


def ask() -> None:
    data = create_user_data()
    text, lang = build_bail_draft(data)
    issues = validate_bail_draft(
        text,
        lang,
        expect_judicial_custody=data.in_judicial_custody,
    )

    print(f"\nOutput language: {lang.upper()}\n")
    if issues:
        print("Checks:", ", ".join(issues))
    print("\n======= FINAL DRAFT =======\n")
    print(text)
    print("\n===========================\n")


if __name__ == "__main__":
    print("\nIndian Law Assistant — bail draft (template)\n")
    ask()
