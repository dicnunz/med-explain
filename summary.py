import sys
import textwrap
from typing import List, Optional

from explain import request_summary, truncate_source_text
from loader import load_text


def summarize(text: str) -> str:
    return request_summary(text)


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entry point — safe to import."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 1:
        sys.stderr.write("Usage: python summary.py <file.pdf>\n")
        sys.exit(1)

    pdf_path = argv[0]
    text = truncate_source_text(load_text(pdf_path))
    result = summarize(text)

    # Write the model summary only (no raw PDF text)
    sys.stdout.write("\nSummary:\n\n")
    sys.stdout.write(textwrap.fill(result, 80) + "\n")


if __name__ == "__main__":  # pragma: no cover
    main()
