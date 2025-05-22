import sys, textwrap
import sys
import textwrap
from typing import List, Optional

from PyPDF2 import PdfReader
master
import ollama
from rich import print
from loader import load_text


pdf_path = sys.argv[1]
text = load_text(pdf_path)[:12000]
def load_text(pdf_path: str) -> str:
    """Extract up to 12 000 chars of text from a PDF."""
    reader = PdfReader(pdf_path)
    return " ".join(page.extract_text() or "" for page in reader.pages)[:12000]


def summarize(text: str) -> str:
    prompt = (
        "Explain the following medical document in 200 words or less so a "
        "12-year-old can understand:\n\n" + text
    )
    resp = ollama.chat(
        model="llama3:8b",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp["message"]["content"]


def main(argv: Optional[List[str]] = None) -> None:
    """Entry point for CLI usage."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("[red]Usage:[/] python summary.py <file.pdf>")
        sys.exit(1)

    pdf_path = argv[0]
    text = load_text(pdf_path)
    result = summarize(text)
    master

    print("\n[bold green]Summary:[/]\n")
    print(textwrap.fill(result, 80))


if __name__ == "__main__":  # pragma: no cover – direct execution
    main()
