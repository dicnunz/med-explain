import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

import streamlit as st

from explain import (
    DEFAULT_MODEL,
    extract_repeated_medical_terms,
    normalize_definition_snippet,
    render_summary_html,
    request_summary,
)
from fhir import build_diagnostic_report
from loader import load_text
from lab_utils import build_lab_chart, parse_lab_results

st.set_page_config(page_title="Med Explain", page_icon="🩺")

# ─────────────────── Session & sidebar history ──────────────────────────────
if "history" not in st.session_state:
    st.session_state.history: List[dict] = []
    st.session_state.selected: int | None = None

st.title("Med Explain")
st.caption(
    "Local-first medical PDF explanations with OCR fallback, optional glossary "
    "tooltips, lab charting, and FHIR JSON export."
)
st.caption(
    "Educational summary only. This app does not diagnose, treat, or replace "
    "a clinician."
)


def build_public_glossary(source_text: str, max_terms: int = 12) -> dict[str, str]:
    from duckduckgo_search import DDGS

    definitions: dict[str, str] = {}
    with DDGS() as ddgs:
        for term in extract_repeated_medical_terms(source_text, max_terms=max_terms):
            hits = ddgs.text(
                f'"{term}" definition site:nih.gov OR site:medlineplus.gov',
                max_results=1,
            )
            if not hits:
                continue

            raw_snippet = hits[0].get("body") or hits[0].get("snippet") or ""
            snippet = normalize_definition_snippet(raw_snippet)
            if snippet:
                definitions[term] = snippet

    return definitions


def build_history_record(
    file_name: str,
    file_digest: str,
    source_text: str,
    glossary_enabled: bool,
) -> tuple[dict, str | None]:
    summary_text = request_summary(source_text)
    glossary: dict[str, str] = {}
    glossary_warning = None
    if glossary_enabled:
        try:
            glossary = build_public_glossary(source_text)
        except Exception:
            glossary_warning = (
                "Summary generated, but glossary lookups failed. The plain-English "
                "summary still ran locally."
            )
    record = {
        "name": file_name,
        "digest": file_digest,
        "summary_html": render_summary_html(summary_text, glossary),
        "summary_text": summary_text,
        "lab_results": parse_lab_results(source_text),
        "diagnostic_report": build_diagnostic_report(summary_text),
    }
    return record, glossary_warning


# ─────────────────── Sidebar History ───────────────────────────────────────
names = [f"{i + 1}. {item['name']}" for i, item in enumerate(st.session_state.history)]
with st.sidebar:
    glossary_enabled = st.checkbox(
        "Add public glossary tooltips",
        value=False,
        help=(
            "Looks up short public definitions for repeated medical terms. "
            "Only the detected terms are sent out, not the full document."
        ),
    )
    st.caption(f"Ollama model: `{DEFAULT_MODEL}`")
    st.caption(
        "Summaries stay local as long as `OLLAMA_HOST` points to your own "
        "Ollama server."
    )

if names:
    choice = st.sidebar.radio(
        "Recent documents",
        names,
        index=st.session_state.selected or 0,
        key="history_radio",
    )
    st.session_state.selected = names.index(choice)
    current_record = st.session_state.history[st.session_state.selected]
else:
    current_record = None

# ─────────────────── PDF uploader  ───────────────────────────────────────────
pdf_file = st.file_uploader("Upload a clinical PDF", type="pdf")
if pdf_file:
    pdf_bytes = pdf_file.getvalue()
    file_digest = hashlib.sha256(pdf_bytes).hexdigest()
    existing_index = next(
        (
            index
            for index, item in enumerate(st.session_state.history)
            if item["digest"] == file_digest
        ),
        None,
    )

    if existing_index is not None:
        st.session_state.selected = existing_index
        current_record = st.session_state.history[existing_index]
    else:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = Path(tmp.name)

        try:
            source_text = load_text(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        if not source_text.strip():
            st.error("No readable text was found in that PDF, even after OCR.")
        else:
            with st.spinner("Summarizing document..."):
                try:
                    current_record, glossary_warning = build_history_record(
                        file_name=pdf_file.name,
                        file_digest=file_digest,
                        source_text=source_text,
                        glossary_enabled=glossary_enabled,
                    )
                except Exception as exc:
                    st.error(
                        "Could not generate a summary. Make sure Ollama is running "
                        f"and that `{DEFAULT_MODEL}` is available."
                    )
                    st.caption(f"Underlying error: {exc}")
                    current_record = None

            if current_record is not None:
                st.session_state.history.append(current_record)
                st.session_state.selected = len(st.session_state.history) - 1
                if glossary_warning:
                    st.info(glossary_warning)

# ─────────────────── Render summary (if any) ────────────────────────────────
if current_record:
    if current_record["lab_results"]:
        st.subheader("Detected Lab Values")
        st.pyplot(build_lab_chart(current_record["lab_results"]))

    st.subheader("Plain-English Summary")
    st.markdown(current_record["summary_html"], unsafe_allow_html=True)
    st.download_button(
        "Download FHIR DiagnosticReport JSON",
        data=json.dumps(current_record["diagnostic_report"], indent=2),
        file_name=f"{Path(current_record['name']).stem}-diagnostic-report.json",
        mime="application/json",
    )
