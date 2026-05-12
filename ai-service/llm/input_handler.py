from typing import Literal

from drafting.schemas import BailDraftInput


def _normalize_language(raw: str) -> Literal["en", "hi", "auto"]:
    s = (raw or "").strip().lower()
    if s in ("hindi", "hi", "हिंदी", "hin"):
        return "hi"
    if s in ("english", "en", "inglish", "angrezi"):
        return "en"
    if s in ("auto", "a", ""):
        return "auto"
    return "auto"


def _parse_custody(raw: str) -> bool:
    s = (raw or "").strip().lower()
    if s in ("n", "no", "0", "false"):
        return False
    return True


def create_user_data() -> BailDraftInput:
    client_name = input("Client name: ").strip()
    court = input("Court: ").strip()
    offence = input("Offence (optional, press Enter to skip): ").strip()
    facts = input("Facts: ").strip()
    language = _normalize_language(input("Output language (english/hindi/auto) [auto]: "))
    custody_in = input("Applicant in judicial custody after arrest? (y/n) [y]: ").strip()
    date_line = input("Date line (optional): ").strip() or None
    place_line = input("Place line (optional): ").strip() or None

    return BailDraftInput(
        client_name=client_name,
        court=court,
        offence=offence,
        facts=facts,
        language=language,
        in_judicial_custody=_parse_custody(custody_in),
        date_line=date_line,
        place_line=place_line,
    )
