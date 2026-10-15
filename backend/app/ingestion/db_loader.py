"""db_loader.py – tabular rows from a CSV file or a SQL table, one sentence per row.

load_db("vendor_contracts.csv")
load_db("vendors", db_url="sqlite:///x.db")   # SQL table (sync SQLAlchemy URL)
"""
import csv
from pathlib import Path


def _row_text(label: str, row_no: int, record: dict) -> str:
    parts = [f"{k}={str(v).strip()}" for k, v in record.items() if v is not None and str(v).strip()]
    return f"{label} | " + " | ".join(parts)


def _csv_rows(path: str):
    with open(path, newline="", encoding="utf-8-sig") as f:
        for rec in csv.DictReader(f):
            yield rec


def _sql_rows(table: str, db_url: str):
    from sqlalchemy import create_engine, text

    if not table.replace("_", "").isalnum():
        raise ValueError(f"invalid table name: {table!r}")
    sync_url = db_url.replace("+asyncpg", "").split("?")[0]
    engine = create_engine(sync_url)
    with engine.connect() as conn:
        for r in conn.execute(text(f"SELECT * FROM {table}")).mappings():
            yield dict(r)


def load_db(path: str, db_url: str | None = None, **_) -> list[dict]:
    is_csv = path.lower().endswith(".csv")
    if is_csv:
        rows, label, name = _csv_rows(path), f"Record", Path(path).name
    else:
        if not db_url:
            raise ValueError("db_url required when loading a SQL table")
        rows, label, name = _sql_rows(path, db_url), f"Table {path}", path

    out = []
    for i, rec in enumerate(rows, start=1):
        # for CSV, row number counts the header as row 1 (spreadsheet convention)
        row_no = i + 1 if is_csv else i
        out.append(
            {
                "text": _row_text(label, row_no, rec),
                "page_or_row": f"row {row_no}",
                "metadata": {"kind": "row", "row": row_no, "file": name},
            }
        )
    return out
