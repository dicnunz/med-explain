import re
import textwrap
from tempfile import NamedTemporaryFile
from typing import List

import streamlit as st
import ollama
from duckduckgo_search import DDGS
from wordfreq import zipf_frequency

from loader import load_text
from lab_utils import build_lab_chart

# ─────────────────── Session & sidebar history ──────────────────────────────
if "history" not in st.session_state:
    st.session_state.history: List[dict] = []
    st.session_state.selected: int | None = None
    st.session_state.last_file: str | None = None

st.title("Med-Explain 📄➡️🧠")

summary_html = None
if st.session_state.history:
    names = [f"{i+1}. {item['name']}" for i, item in enumerate(st.session_state.history)] # noqa: E501
    choice = st.sidebar.radio(
        "History", names, index=st.session_state.selected or 0, key="history_radio"
    )
    st.session_state.selected = names.index(choice)
    summary_html = st.session_state.history[st.session_state.selected]["summary"]

# ─────────────────── PDF uploader  ───────────────────────────────────────────
pdf_file = st.file_uploader("Upload a medical PDF", type="pdf")
if pdf_file:
    # Avoid re-running on the same file
    if pdf_file.name != st.session_state.last_file:
        with NamedTemporaryFile(delete=False) as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name

        text = load_text(tmp_path)
        if not text.strip():
            st.error("No extractable text found — try another PDF.")
        else:
            # ---------------- glossary / tooltips -----------------
            from duckduckgo_search import DDGS  # local import keeps startup fast

            def build_glossary(src: str, max_terms: int = 20) -> dict[str, str]:
                words = re.findall(r"[A-Za-z]{6,}", src.lower())
                counts = {}
                for w in words:
                    if zipf_frequency(w, "en") < 4:
                        counts[w] = counts.get(w, 0) + 1
                common = sorted(
                    (w for w, c in counts.items() if c >= 2),
                    key=lambda x: -counts[x],
                )[:max_terms]

                defs: dict[str, str] = {}
                with DDGS() as ddgs:
                    for w in common:
                        try:
                            res = next(
                                ddgs.text(f"{w} medical definition", max_results=1)
                            )
                            body = res.get("body") or res.get("snippet") or ""
                            defs[w] = body.split(".")[0] + "…"
                        except StopIteration:
                            pass
                return defs

            glossary = build_glossary(text)

            def with_tooltips(markup: str) -> str:
                for w, tip in glossary.items():
                    pat = rf"\b({w})\b"
                    rep = (
                        rf'<span title="{tip}" '
                        rf'style="border-bottom:1px dotted #888;cursor:help;">\1</span>'
                    )
                    markup = re.sub(pat, rep, markup, flags=re.I)
                return markup

            # ---------------- summarise ---------------------------
            prompt = (
                "Explain the following medical document in ≤200 words so a "
                "12-year-old can understand:\n\n"
            )
            resp = ollama.chat(
                model="llama3:8b",
                messages=[{"role": "user", "content": prompt + text[:12_000]}],
            )
            summary_text = textwrap.fill(resp["message"]["content"], 80)
            summary_html = with_tooltips(summary_text)

            st.session_state.history.append(
                {"name": pdf_file.name, "summary": summary_html}
            )
            st.session_state.selected = len(st.session_state.history) - 1
            st.session_state.last_file = pdf_file.name

            # ---------------- bar chart if labs present ------------
            fig = build_lab_chart(text)
            if fig:
                st.pyplot(fig)

# ─────────────────── Render summary (if any) ────────────────────────────────
if summary_html:
    st.subheader("Summary")
    st.markdown(summary_html, unsafe_allow_html=True)
