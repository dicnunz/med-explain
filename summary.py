import sys
import textwrap
from typing import List, Optional

import ollama

from loader import load_text


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
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        print("[red]Usage:[/] python summary.py <file.pdf>")
        sys.exit(1)

    pdf_path = argv[0]
    text = load_text(pdf_path)[:12_000]
    result = summarize(text)

    print("\n[bold green]Summary:[/]\n")
    print(textwrap.fill(result, 80))


if __name__ == "__main__":  # pragma: no cover
    main()
