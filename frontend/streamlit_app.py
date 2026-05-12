"""
LAWASSIST Streamlit UI — calls FastAPI in ai-service (Legal Q&A + bail drafting).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_REPO_ROOT / ".env")

EXAMPLES_PATH = _REPO_ROOT / "ai-service" / "examples" / "rag_qa_samples.json"


def _default_api_base() -> str:
    return os.getenv("LAWASSIST_API_BASE", "http://127.0.0.1:8000").strip().rstrip("/")


def _load_sample_questions() -> list[dict]:
    if not EXAMPLES_PATH.is_file():
        return []
    try:
        data = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict) and x.get("question")]


st.set_page_config(page_title="LAWASSIST", layout="wide")

st.title("LAWASSIST")
st.caption("Indian legal Q&A (RAG) and bail application drafting — UI only; API runs separately.")

with st.sidebar:
    st.header("API")
    api_base = st.text_input(
        "FastAPI base URL",
        value=_default_api_base(),
        help="Where uvicorn serves main:app (e.g. http://127.0.0.1:8000)",
    ).strip().rstrip("/")
    if st.button("Check API"):
        try:
            r = httpx.get(f"{api_base}/", timeout=5.0)
            st.success(r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text)
        except httpx.RequestError as e:
            st.error(str(e))

tab_qa, tab_bail = st.tabs(["Legal Q&A", "Bail draft"])

# --- Legal Q&A ---
with tab_qa:
    samples = _load_sample_questions()
    if samples:
        id_opts = [s.get("id", f"sample-{i}") for i, s in enumerate(samples)]
        pick = st.selectbox("Example (optional)", ["—"] + id_opts, key="qa_sample_pick")
        if st.button("Insert example into question box", key="qa_insert"):
            if pick != "—":
                chosen = next((s for s in samples if s.get("id") == pick), None)
                if chosen:
                    st.session_state["qa_question"] = chosen.get("question", "")
                    st.rerun()

    question = st.text_area("Your question", height=120, key="qa_question")

    if st.button("Ask", type="primary", key="ask_btn"):
        if not question.strip():
            st.warning("Enter a question.")
        else:
            with st.spinner("Calling /ask …"):
                try:
                    r = httpx.post(
                        f"{api_base}/ask",
                        json={"q": question.strip()},
                        timeout=120.0,
                    )
                    if r.status_code != 200:
                        st.error(f"HTTP {r.status_code}")
                        st.code(r.text)
                    else:
                        data = r.json()
                        st.subheader("Answer")
                        st.markdown(data.get("answer", "(empty)"))
                except httpx.RequestError as e:
                    st.error(f"Request failed: {e}")

# --- Bail ---
with tab_bail:
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client / applicant name", key="bail_name")
        court = st.text_input("Court", key="bail_court")
        offence = st.text_input("Offence (optional)", key="bail_offence")
    with col2:
        language = st.selectbox("Output language", ["auto", "en", "hi"], index=0, key="bail_lang")
        in_judicial_custody = st.checkbox("In judicial custody after arrest", value=True, key="bail_custody")
        date_line = st.text_input("Date line (optional)", key="bail_date")
        place_line = st.text_input("Place line (optional)", key="bail_place")
    facts = st.text_area("Facts", height=160, key="bail_facts")

    if st.button("Generate bail draft", type="primary", key="bail_btn"):
        missing = []
        if not (client_name or "").strip():
            missing.append("client name")
        if not (court or "").strip():
            missing.append("court")
        if not (facts or "").strip():
            missing.append("facts")
        if missing:
            st.warning("Fill in: " + ", ".join(missing))
        else:
            payload = {
                "client_name": client_name.strip(),
                "court": court.strip(),
                "offence": (offence or "").strip(),
                "facts": facts.strip(),
                "language": language,
                "in_judicial_custody": in_judicial_custody,
                "date_line": (date_line or "").strip() or None,
                "place_line": (place_line or "").strip() or None,
            }
            with st.spinner("Calling /draft/bail …"):
                try:
                    r = httpx.post(
                        f"{api_base}/draft/bail",
                        json=payload,
                        timeout=60.0,
                    )
                    if r.status_code != 200:
                        st.error(f"HTTP {r.status_code}")
                        st.code(r.text)
                    else:
                        data = r.json()
                        issues = data.get("issues") or []
                        if issues:
                            st.warning("Checks: " + "; ".join(str(i) for i in issues))
                        st.subheader(f"Draft ({data.get('language', '')})")
                        draft = data.get("draft", "")
                        st.code(draft)
                        st.download_button(
                            "Download .txt",
                            data=draft,
                            file_name="bail_application.txt",
                            mime="text/plain",
                            key="bail_dl",
                        )
                except httpx.RequestError as e:
                    st.error(f"Request failed: {e}")

st.divider()
st.markdown(
    """
**Disclaimer:** This tool is for informational and educational use only. It is not legal advice.
Verify all citations and final drafts with a qualified advocate. Bail output uses a fixed template;
facts are your responsibility.
"""
)
