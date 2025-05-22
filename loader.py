import io
from pathlib import Path
from typing import Union

from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import pytesseract
from PIL import Image


PathLike = Union[str, bytes, Path]

def _extract_with_pypdf2(path: PathLike) -> str:
    reader = PdfReader(path)
    return " ".join(page.extract_text() or "" for page in reader.pages)

def _extract_with_ocr(path: PathLike) -> str:
    doc = fitz.open(path)
    texts = []
    for page in doc:
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        texts.append(pytesseract.image_to_string(img))
    doc.close()
    return "\n".join(texts)

def load_text(path: PathLike) -> str:
    text = _extract_with_pypdf2(path)
    if text.strip():
        return text
    return _extract_with_ocr(path)
