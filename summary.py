import sys, textwrap
import ollama
from rich import print
from loader import load_text

if len(sys.argv) != 2:
    print("[red]Usage:[/] python summary.py <file.pdf>")
    sys.exit(1)

pdf_path = sys.argv[1]
text = load_text(pdf_path)[:12000]

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