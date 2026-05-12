"""
Deterministic Indian court-style bail application shells (English + Hindi).
User-supplied fields are concatenated (not f-string interpolated) to avoid brace issues in facts.
"""

from __future__ import annotations

from typing import Literal

try:
    from langdetect import detect as _langdetect_detect
except ImportError:
    _langdetect_detect = None

from drafting.schemas import BailDraftInput

# Markers used by validation (subset must appear in rendered output)
REQUIRED_MARKERS_EN = (
    "BAIL APPLICATION",
    "IN THE COURT OF",
    "MOST RESPECTFULLY SHOWETH:",
    "GROUNDS:",
    "PRAYER:",
)

REQUIRED_MARKERS_HI = (
    "जमानत आवेदन पत्र",
    "महोदय,",
    "आधार:",
    "अतः प्रार्थना है",
)

GROUNDS_EN = """1. No prior criminal record.
2. Not likely to abscond.
3. Will not tamper with evidence.
4. Further custody not required.
5. Offence not of serious nature."""

GROUNDS_HI = """1. कोई पूर्व आपराधिक इतिहास नहीं
2. फरार होने की संभावना नहीं
3. साक्ष्य से छेड़छाड़ की संभावना नहीं
4. आगे की हिरासत आवश्यक नहीं
5. अपराध गंभीर प्रकृति का नहीं"""


def detect_language_from_text(text: str) -> Literal["en", "hi"]:
    if _langdetect_detect is None:
        return "en"
    try:
        if _langdetect_detect(text) == "hi":
            return "hi"
    except Exception:
        pass
    return "en"


def resolve_output_language(data: BailDraftInput) -> Literal["en", "hi"]:
    if data.language == "en":
        return "en"
    if data.language == "hi":
        return "hi"
    combined = (data.offence or "") + " " + (data.facts or "")
    return detect_language_from_text(combined)


def _offence_clause_en(offence: str) -> str:
    o = (offence or "").strip()
    if not o:
        return ""
    return "The applicant is accused of " + o + ". "


def _offence_clause_hi(offence: str) -> str:
    o = (offence or "").strip()
    if not o:
        return ""
    return "अभियुक्त के विरुद्ध " + o + " का आरोप है। "


def render_bail_en(data: BailDraftInput) -> str:
    court = (data.court or "").strip()
    name = (data.client_name or "").strip()
    facts = (data.facts or "").strip()
    date_line = (data.date_line or "").strip()
    place_line = (data.place_line or "").strip()

    parts: list[str] = [
        "The applicant, ",
        name,
        ", respectfully submits as under:\n\n",
        _offence_clause_en(data.offence or ""),
        facts,
    ]
    if data.in_judicial_custody:
        parts.append(
            "\n\nThe applicant was taken into police custody and is presently in judicial custody."
        )
    opening = "".join(parts).strip()

    draft = (
        "BAIL APPLICATION\n\n"
        + "IN THE COURT OF "
        + court
        + "\n\n"
        + "MOST RESPECTFULLY SHOWETH:\n\n"
        + opening
        + "\n\n"
        + "GROUNDS:\n\n"
        + GROUNDS_EN
        + "\n\n"
        + "PRAYER:\n\n"
        + "It is therefore most respectfully prayed that this Hon'ble Court may be pleased to grant bail to the applicant.\n\n"
        + "Date: "
        + date_line
        + "\n"
        + "Place: "
        + place_line
        + "\n\n"
        + "Counsel for the Applicant\n"
    )
    return draft.strip() + "\n"


def render_bail_hi(data: BailDraftInput) -> str:
    court = (data.court or "").strip()
    name = (data.client_name or "").strip()
    facts = (data.facts or "").strip()
    date_line = (data.date_line or "").strip()
    place_line = (data.place_line or "").strip()

    parts_hi: list[str] = [
        "अभियुक्त ",
        name,
        " के संबंध में। ",
        _offence_clause_hi(data.offence or ""),
        facts,
    ]
    if data.in_judicial_custody:
        parts_hi.append(
            "\n\nअभियुक्त को पुलिस द्वारा गिरफ्तार किया गया है तथा वह वर्तमान में न्यायिक हिरासत में है।"
        )
    body = "".join(parts_hi).strip()

    draft = (
        "जमानत आवेदन पत्र\n\n"
        + "माननीय न्यायिक मजिस्ट्रेट न्यायालय, "
        + court
        + "\n\n"
        + "महोदय,\n\n"
        + body
        + "\n\n"
        + "आधार:\n\n"
        + GROUNDS_HI
        + "\n\n"
        + "अतः प्रार्थना है कि माननीय न्यायालय अभियुक्त को जमानत प्रदान करने की कृपा करें।\n\n"
        + "दिनांक: "
        + date_line
        + "\n"
        + "स्थान: "
        + place_line
        + "\n\n"
        + "अधिवक्ता\n"
    )
    return draft.strip() + "\n"


def build_bail_draft(data: BailDraftInput) -> tuple[str, Literal["en", "hi"]]:
    lang = resolve_output_language(data)
    if lang == "hi":
        return render_bail_hi(data), "hi"
    return render_bail_en(data), "en"


def validate_bail_draft(
    text: str,
    lang: Literal["en", "hi"],
    *,
    expect_judicial_custody: bool = True,
) -> list[str]:
    """Structural and lightweight safety checks (no LLM)."""
    issues: list[str] = []
    t = text or ""

    markers = REQUIRED_MARKERS_EN if lang == "en" else REQUIRED_MARKERS_HI
    for m in markers:
        if m not in t:
            issues.append(f"Missing marker: {m}")

    if any(x in t for x in ["मैं", "मेरे", "मेरा", "हम"]):
        issues.append("First person (Hindi) detected")

    if lang == "en":
        lower = " " + t.lower() + " "
        if (
            " i " in lower
            or " i'm " in lower
            or " we " in lower
            or " we've " in lower
            or lower.startswith("i ")
        ):
            issues.append("First person (English) detected")

    if any(x in t for x in ["स्वीकार", "पश्चाताप"]) and "न स्वीकार" not in t:
        issues.append("Confession-related wording (Hindi)")

    if lang == "en" and "confess" in t.lower():
        issues.append("Confession-related wording (English)")

    if lang == "hi" and expect_judicial_custody and "न्यायिक हिरासत" not in t:
        issues.append("Missing judicial custody (Hindi)")

    if lang == "en" and expect_judicial_custody and "judicial custody" not in t.lower():
        issues.append("Missing judicial custody (English)")

    return issues
