"""registry.py – source_type -> loader."""
from typing import Callable

from app.ingestion.db_loader import load_db
from app.ingestion.pdf_loader import load_pdf
from app.ingestion.web_loader import load_web
from app.ingestion.xlsx_loader import load_xlsx

LOADERS: dict[str, Callable[..., list[dict]]] = {
    "pdf": load_pdf,
    "xlsx": load_xlsx,
    "html": load_web,
    "web": load_web,
    "csv": load_db,
    "db": load_db,
}

EXT_TO_TYPE = {".pdf": "pdf", ".xlsx": "xlsx", ".html": "html", ".htm": "html", ".csv": "csv"}


def get_loader(source_type: str) -> Callable[..., list[dict]]:
    try:
        return LOADERS[source_type.lower()]
    except KeyError:
        raise ValueError(f"No loader for source_type={source_type!r}; known: {sorted(LOADERS)}")


def guess_source_type(filename: str) -> str:
    import os

    ext = os.path.splitext(filename)[1].lower()
    if ext not in EXT_TO_TYPE:
        raise ValueError(f"Unsupported file extension {ext!r}")
    return EXT_TO_TYPE[ext]
