import pytest
from pathlib import Path
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.xlsx_loader import load_xlsx
from app.ingestion.db_loader import load_db
from app.ingestion.web_loader import load_web

RAW_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "raw"

def test_pdf_connector():
    pdf_path = RAW_DIR / "policy_handbook_v2_2024.pdf"
    assert pdf_path.exists(), f"PDF file not found at {pdf_path}"
    
    segments = load_pdf(str(pdf_path))
    assert len(segments) > 0, "PDF loader returned empty segments"
    for seg in segments:
        assert seg["text"].strip(), "Segment text is empty"
        assert seg["page_or_row"].startswith("page "), f"Invalid page_or_row: {seg['page_or_row']}"
        assert "file" in seg["metadata"]
        assert seg["metadata"]["page"] >= 1
    # Check that key content is present
    full_text = " ".join(s["text"] for s in segments)
    assert "remote" in full_text.lower() or "policy" in full_text.lower()

def test_xlsx_connector():
    xlsx_path = RAW_DIR / "q3_sales_headcount.xlsx"
    assert xlsx_path.exists(), f"XLSX file not found at {xlsx_path}"
    
    segments = load_xlsx(str(xlsx_path))
    assert len(segments) > 0, "XLSX loader returned empty segments"
    for seg in segments:
        text = seg["text"]
        assert text.strip(), "Segment text is empty"
        assert seg["page_or_row"].startswith("row "), f"Invalid row indicator: {seg['page_or_row']}"
        # Verify row/column context preservation: "Sheet ... | Header=Value"
        assert "Sheet " in text, f"Sheet context missing in: {text}"
        assert "=" in text, f"Column=Value context missing in: {text}"
        assert "row" in seg["metadata"]
        assert "sheet" in seg["metadata"]

def test_csv_connector():
    csv_path = RAW_DIR / "vendor_contracts.csv"
    assert csv_path.exists(), f"CSV file not found at {csv_path}"
    
    segments = load_db(str(csv_path))
    assert len(segments) > 0, "CSV loader returned empty segments"
    for seg in segments:
        text = seg["text"]
        assert text.strip(), "Segment text is empty"
        assert seg["page_or_row"].startswith("row "), f"Invalid row indicator: {seg['page_or_row']}"
        assert "=" in text, f"Key-value context missing in: {text}"
        assert seg["metadata"]["row"] >= 2 # row 1 is header

def test_web_connector():
    html_path = RAW_DIR / "it_security_policy.html"
    assert html_path.exists(), f"HTML file not found at {html_path}"
    
    segments = load_web(str(html_path))
    assert len(segments) > 0, "Web loader returned empty segments"
    for seg in segments:
        text = seg["text"]
        assert text.strip(), "Segment text is empty"
        assert seg["page_or_row"].startswith("section "), f"Invalid section indicator: {seg['page_or_row']}"
        assert "heading" in seg["metadata"]
    # Check table structure if tables are present
    full_text = " ".join(s["text"] for s in segments)
    assert "password" in full_text.lower() or "security" in full_text.lower()
