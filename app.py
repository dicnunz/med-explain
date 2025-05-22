import re
import textwrap
from tempfile import NamedTemporaryFile

import streamlit as st
import ollama
from duckduckgo_search import DDGS
from wordfreq import zipf_frequency

from loader import load_text

st.title("Med-Explain 📄➡️🧠")

pdf_file = st.file_uploader("Upload a medical PDF", type="pdf")
if pdf_file:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name
    text = load_text(tmp_path)[:12000]
    # ---- Identify likely medical jargon ----------------------------------
    words = re.findall(r"[A-Za-z]{6,}", text.lower())  # 6+ letters
    counts = {}
    for w in words:
        # skip very common English words (Zipf freq ≥ 4 means everyday word)
        if zipf_frequency(w, "en") < 4:
            counts[w] = counts.get(w, 0) + 1

    # keep words that appear at least twice and take the 30 most frequent
    common = sorted((w for w, c in counts.items() if c >= 2), key=lambda x: -counts[x])[
        :30
    ]

    def explain(term):
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(
                    f"{term} medical definition",
                    region="us-en",
                    safesearch="on",
                    max_results=1,
                ):
                    body = r.get("body") or r.get("snippet") or ""
                    if body:
                        return body.split(".")[0] + "..."
        except Exception:
            pass
        return None  # no definition found

    glossary = {}
    for w in common:
        tip = explain(w)
        if tip:  # only keep words with a real definition
            glossary[w] = tip
    if not text.strip():
        st.error("No extractable text found – try another PDF.")
    else:
        with st.spinner("Summarizing…"):
            resp = ollama.chat(
                model="llama3:8b",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Explain this medical document in 200 words "
                            "so a 12-year-old can understand:\n\n" + text
                        ),
                    }
                ],
            )

            def with_tooltips(text_):
                for w, tip in glossary.items():
                    pattern = rf"\b({w})\b"
                    replacement = (
                        rf'<span title="{tip}" '
                        rf'style="border-bottom:1px dotted #888;cursor:help;">'
                        "\\1</span>"
                    )
                    text_ = re.sub(pattern, replacement, text_, flags=re.I)
                return text_

        st.subheader("Summary")
        summary_text = textwrap.fill(resp["message"]["content"], 80)
        st.markdown(with_tooltips(summary_text), unsafe_allow_html=True)
