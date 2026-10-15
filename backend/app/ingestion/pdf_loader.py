"""pdf_loader.py – extract text per page, keeping 1-based page numbers."""
from pathlib import Path


def _pages_pdfplumber(path: str) -> list[str]:
    import pdfplumber

    out = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            out.append(page.extract_text() or "")
    return out


def _pages_pypdf(path: str) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:  # PyPDF2 is what requirements.txt pins
        from PyPDF2 import PdfReader
    return [(p.extract_text() or "") for p in PdfReader(path).pages]


def load_pdf(path: str, **_) -> list[dict]:
    try:
        pages = _pages_pdfplumber(path)
    except ImportError:
        pages = _pages_pypdf(path)

    name = Path(path).name
    return [
        {
            "text": text.strip(),
            "page_or_row": f"page {i}",
            "metadata": {"kind": "page", "page": i, "file": name},
        }
        for i, text in enumerate(pages, start=1)
        if text.strip()
    ]
