# Med Explain

Med Explain turns clinical PDFs into plain-English summaries on your own
machine. It extracts text from native PDFs, falls back to OCR for scanned
pages, uses a local Ollama model to explain the document, highlights repeated
medical jargon with optional glossary tooltips, and can export the result as a
FHIR `DiagnosticReport` JSON file.

This is a deliberately small repo, but it demonstrates a useful healthcare AI
workflow end to end: local-first inference, OCR fallback, lightweight lab-value
parsing, and interoperability-aware output.

## What It Does

- explains lab reports and clinical notes in plain English
- handles scanned PDFs with a Tesseract OCR fallback
- detects simple lab values and plots them against reference ranges
- stores recent uploads in the session so you can compare documents
- exports the generated explanation as a minimal US Core-style FHIR payload

## Quick Start

### Docker Compose

```bash
docker compose up --build -d
docker compose exec ollama ollama pull llama3:8b
open http://localhost:8501
```

To stop the stack:

```bash
docker compose down
```

If you want a different local model, set `MED_EXPLAIN_MODEL` before starting
the stack.

### Local Python Run

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install tesseract
ollama serve
ollama pull llama3:8b
streamlit run app.py
```

## Architecture

1. `loader.py` extracts embedded text with `PyPDF2`.
2. If the PDF is image-only, `loader.py` renders pages with `PyMuPDF` and runs
   OCR through Tesseract.
3. `app.py` calls Ollama for the plain-English summary, optionally enriches
   repeated medical terms with short public glossary snippets, and plots basic
   lab values.
4. `fhir.py` packages the explanation as a portable `DiagnosticReport` JSON
   download.
5. `summary.py` exposes the summarizer as a simple CLI for batch or scripted use.

## Privacy And Data Handling

- The main summary flow is local as long as `OLLAMA_HOST` points to your own
  Ollama server.
- Uploaded PDFs are written to a temporary file for extraction and then deleted
  immediately.
- Optional glossary tooltips are the only networked feature. They send repeated
  candidate terms like `hemoglobin` or `triglycerides` to public sources for
  short definitions; the full document does not leave the machine.
- This project is not HIPAA-compliant infrastructure. There is no built-in
  encryption, access control, audit trail, or clinical validation layer.

## Limitations

- The summary is educational, not medical advice.
- Lab parsing is intentionally shallow and only covers a few common value/unit
  patterns.
- OCR quality depends heavily on scan quality.
- The FHIR export is intentionally minimal and should be treated as an example,
  not a production integration.
- The glossary feature relies on public web snippets and may miss terms or
  return imperfect definitions.

## Safe Demo Asset

Use [examples/synthetic-lab-report.md](examples/synthetic-lab-report.md) for a
safe demo. It contains invented data only. Open it locally, print it to PDF,
and upload that PDF to the app.

## Checks

```bash
ruff check .
black --check .
pytest -q
```

