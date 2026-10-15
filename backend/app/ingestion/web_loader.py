"""web_loader.py – parse HTML (local file or URL) into heading-delimited sections.

Table rows are rendered one per line as "cell | cell | cell" so the chunker can
treat each as an atomic row.
"""
from pathlib import Path

from bs4 import BeautifulSoup

_HEADINGS = ("h1", "h2", "h3")
_BLOCKS = ("p", "li", "tr", "pre", "blockquote", "h4", "h5", "h6")


def _read(src: str) -> tuple[str, str]:
    if src.startswith(("http://", "https://")):
        import requests

        r = requests.get(src, timeout=30, headers={"User-Agent": "rag-ingest/1.0"})
        r.raise_for_status()
        return r.text, src
    return Path(src).read_text(encoding="utf-8", errors="replace"), Path(src).name


def load_web(path: str, **_) -> list[dict]:
    html, name = _read(path)
    soup = BeautifulSoup(html, "lxml") if _has_lxml() else BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "nav", "footer"]):
        t.decompose()
    root = soup.body or soup

    sections: list[tuple[str, list[str]]] = [("Introduction", [])]
    for el in root.find_all(list(_HEADINGS) + list(_BLOCKS)):
        if el.name in _HEADINGS:
            sections.append((el.get_text(" ", strip=True), []))
            continue
        if el.name == "li" and el.find(["li", "tr"]):
            continue
        if el.name == "p" and el.find_parent("tr"):
            continue
        if el.name == "tr":
            cells = [c.get_text(" ", strip=True) for c in el.find_all(["th", "td"])]
            line = " | ".join(c for c in cells if c)
        else:
            line = el.get_text(" ", strip=True)
        if line:
            sections[-1][1].append(line)

    out = []
    n = 0
    for heading, lines in sections:
        if not lines:
            continue
        n += 1
        out.append(
            {
                "text": heading + "\n" + "\n".join(lines),
                "page_or_row": f"section {n}",
                "metadata": {"kind": "section", "section": n, "heading": heading, "file": name},
            }
        )
    return out


def _has_lxml() -> bool:
    try:
        import lxml  # noqa: F401
        return True
    except ImportError:
        return False
