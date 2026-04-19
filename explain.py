import html
import os
import re
from collections import Counter
from typing import Mapping

import ollama
from wordfreq import zipf_frequency

DEFAULT_MODEL = os.getenv("MED_EXPLAIN_MODEL", "llama3:8b")
SOURCE_TEXT_LIMIT = 12_000
TOOLTIP_STYLE = "border-bottom:1px dotted #888;cursor:help;"


def truncate_source_text(text: str, limit: int = SOURCE_TEXT_LIMIT) -> str:
    return text[:limit].strip()


def build_plain_language_prompt(text: str) -> str:
    excerpt = truncate_source_text(text)
    return (
        "You are explaining a medical document in plain English.\n"
        "Write 200 words or less for a curious 12-year-old.\n"
        "Focus on the main findings, whether anything looks high or low, "
        "and what would be reasonable to ask a clinician next.\n"
        "Do not invent diagnoses, treatments, or certainty that is not in the "
        "document.\n\n"
        f"Medical document:\n{excerpt}"
    )


def request_summary(text: str, model: str = DEFAULT_MODEL) -> str:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": build_plain_language_prompt(text)}],
    )
    return response["message"]["content"].strip()


def extract_repeated_medical_terms(text: str, max_terms: int = 20) -> list[str]:
    words = re.findall(r"[A-Za-z]{6,}", text.lower())
    counts = Counter(word for word in words if zipf_frequency(word, "en") < 4)
    ranked_terms = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [term for term, count in ranked_terms if count >= 2][:max_terms]


def normalize_definition_snippet(snippet: str) -> str:
    cleaned = " ".join(snippet.split())
    if not cleaned:
        return ""

    first_sentence = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0]
    trimmed = first_sentence.rstrip(".!?")
    if len(trimmed) > 160:
        trimmed = trimmed[:157].rsplit(" ", 1)[0]
    return f"{trimmed}..."


def render_summary_html(summary_text: str, glossary: Mapping[str, str]) -> str:
    rendered = html.escape(summary_text)
    for term, definition in sorted(glossary.items(), key=lambda item: -len(item[0])):
        safe_definition = html.escape(definition, quote=True)
        pattern = re.compile(rf"\b({re.escape(term)})\b", re.IGNORECASE)
        rendered = pattern.sub(
            lambda match: (
                f'<span title="{safe_definition}" style="{TOOLTIP_STYLE}">'
                f"{match.group(0)}</span>"
            ),
            rendered,
        )
    return rendered.replace("\n", "<br>")
