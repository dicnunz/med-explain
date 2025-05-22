import sys, textwrap
from PyPDF2 import PdfReader
import ollama
from rich import print

if len(sys.argv) != 2:
    print("[red]Usage:[/] python summary.py <file.pdf>")
    sys.exit(1)

pdf_path = sys.argv[1]
reader   = PdfReader(pdf_path)
text     = " ".join(page.extract_text() or "" for page in reader.pages)[:12000]

prompt = (
    "Explain the following medical document in 200 words or less so a "
    "12-year-old can understand:\n\n" + text
)

resp = ollama.chat(
    model="llama3:8b",
    messages=[{"role": "user", "content": prompt}],
)

print("\n[bold green]Summary:[/]\n")
print(textwrap.fill(resp["message"]["content"], 80))