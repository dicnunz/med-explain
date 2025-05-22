import streamlit as st
import ollama, textwrap
from PyPDF2 import PdfReader
import re
from wordfreq import zipf_frequency
from duckduckgo_search import DDGS

st.title("Med-Explain 📄➡️🧠")

# Initialize history of uploaded summaries in the session
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"name": str, "summary": str}
if "selected" not in st.session_state:
    st.session_state.selected = None
if "last_file" not in st.session_state:
    st.session_state.last_file = None

# Sidebar to navigate previous summaries
summary_html = None
if st.session_state.history:
    names = [f"{i+1}. {item['name']}" for i, item in enumerate(st.session_state.history)]
    choice = st.sidebar.radio("History", names, index=st.session_state.selected or 0, key="history_radio")
    st.session_state.selected = names.index(choice)
    summary_html = st.session_state.history[st.session_state.selected]["summary"]
else:
    st.sidebar.write("No summaries yet.")

pdf_file = st.file_uploader("Upload a medical PDF", type="pdf")
if pdf_file and pdf_file.name != st.session_state.last_file:
    reader = PdfReader(pdf_file)
    text = " ".join(page.extract_text() or "" for page in reader.pages)[:12000]
    # ---- Identify likely medical jargon ----------------------------------
    words = re.findall(r"[A-Za-z]{6,}", text.lower())          # 6+ letters
    counts = {}
    for w in words:
        # skip very common English words (Zipf freq ≥ 4 means everyday word)
        if zipf_frequency(w, "en") < 4:
            counts[w] = counts.get(w, 0) + 1

    # keep words that appear at least twice and take the 30 most frequent
    common = sorted(
        (w for w, c in counts.items() if c >= 2),
        key=lambda x: -counts[x]
    )[:30]

    def explain(term):
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(f"{term} medical definition", region="us-en",
                                   safesearch="on", max_results=1):
                    body = r.get("body") or r.get("snippet") or ""
                    if body:
                        return body.split(".")[0] + "..."
        except Exception:
            pass
        return None  # no definition found

    glossary = {}
    for w in common:
        tip = explain(w)
        if tip:                       # only keep words with a real definition
            glossary[w] = tip

    if not text.strip():
        st.error("No extractable text found – try another PDF.")
    else:
        with st.spinner("Summarizing…"):
            resp = ollama.chat(
                model="llama3:8b",
                messages=[{"role": "user",
                           "content": ("Explain this medical document in 200 words "
                                       "so a 12-year-old can understand:\n\n" + text)}],
            )

        def with_tooltips(text_):
            for w, tip in glossary.items():
                pattern = rf'\b({w})\b'
                replacement = rf'<span title="{tip}" style="border-bottom:1px dotted #888;cursor:help;">\1</span>'
                text_ = re.sub(pattern, replacement, text_, flags=re.I)
            return text_

        summary_text = textwrap.fill(resp["message"]["content"], 80)
        summary_html = with_tooltips(summary_text)
        st.session_state.history.append({"name": pdf_file.name, "summary": summary_html})
        st.session_state.selected = len(st.session_state.history) - 1
        st.session_state.last_file = pdf_file.name

if summary_html:
    st.subheader("Summary")
    st.markdown(summary_html, unsafe_allow_html=True)
