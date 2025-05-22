import sys
import textwrap
from typing import List, Optional

from rich import print
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
    """CLI entry point — safe to import."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        sys.stderr.write("[red]Usage:[/] python summary.py <file.pdf>\n")
        sys.exit(1)

    pdf_path = argv[0]
    text = load_text(pdf_path)[:12_000]
    result = summarize(text)

    # Write the model summary only (no raw PDF text)
    sys.stdout.write("\nSummary:\n\n")
    sys.stdout.write(textwrap.fill(result, 80) + "\n")


if __name__ == "__main__":  # pragma: no cover
    main()
