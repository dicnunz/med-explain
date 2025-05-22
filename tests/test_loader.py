import os
import sys
import fitz
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from loader import load_text


def create_pdf_with_text(path, text):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def create_empty_pdf(path):
    doc = fitz.open()
    doc.new_page()
    doc.save(path)
    doc.close()


def create_scanned_pdf(path, text):
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((50, 80), text, fill='black')
    img_path = path.with_suffix('.png')
    img.save(img_path)
    doc = fitz.open()
    page = doc.new_page(width=400, height=200)
    page.insert_image(page.rect, filename=img_path)
    doc.save(path)
    doc.close()
    os.remove(img_path)


def test_normal_pdf(tmp_path):
    pdf = tmp_path / "normal.pdf"
    create_pdf_with_text(pdf, "Hello World")
    text = load_text(pdf)
    assert "Hello World" in text


def test_empty_pdf(tmp_path):
    pdf = tmp_path / "empty.pdf"
    create_empty_pdf(pdf)
    text = load_text(pdf)
    assert text.strip() == ""


def test_scanned_pdf(tmp_path):
    pdf = tmp_path / "scan.pdf"
    create_scanned_pdf(pdf, "OCR Test")
    text = load_text(pdf)
    assert "Test" in text
