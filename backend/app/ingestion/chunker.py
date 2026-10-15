"""chunker.py – recursive, row-safe chunking.

* Size is measured in whitespace-delimited tokens (cheap approximation of model tokens).
* Page/section segments are split recursively: paragraph -> line -> sentence -> word.
* A "table row" (a single line containing ' | ' or a tab, or a loader row segment)
  is atomic and is never split, even if it exceeds the target size.
* Overlap is made from whole trailing units only, so no unit is ever cut.
* Each chunk text is prefixed with "[Title | v{version} | {date}]".
"""
CHUNK_TOKENS = 400
CHUNK_OVERLAP = 60

_SEPS = ["\n\n", "\n", ". ", " "]


def count_tokens(text: str) -> int:
    return len(text.split())


def is_table_row(text: str) -> bool:
    return "\n" not in text and (text.count(" | ") >= 2 or "\t" in text)


def _split(text: str, size: int, level: int = 0) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if count_tokens(text) <= size or is_table_row(text) or level >= len(_SEPS):
        return [text]
    sep = _SEPS[level]
    parts = text.split(sep)
    if sep == ". ":  # keep the full stop with its sentence
        parts = [p + "." if i < len(parts) - 1 else p for i, p in enumerate(parts)]
    out: list[str] = []
    for p in parts:
        out.extend(_split(p, size, level + 1))
    return out


def _merge(units: list[str], size: int, overlap: int) -> list[tuple[int, int]]:
    """Greedy packing -> list of (start, end_exclusive) unit index ranges."""
    groups: list[tuple[int, int]] = []
    n = len(units)
    start = 0
    while start < n:
        end, total = start, 0
        while end < n:
            t = count_tokens(units[end])
            if end > start and total + t > size:
                break
            total += t
            end += 1
        groups.append((start, end))
        if end >= n:
            break
        # overlap: step back over whole trailing units up to `overlap` tokens
        nxt, ov = end, 0
        while nxt - 1 > start and ov + count_tokens(units[nxt - 1]) <= overlap:
            nxt -= 1
            ov += count_tokens(units[nxt])
        start = nxt
    return groups


def make_prefix(title: str, version: str | None, doc_date: str | None) -> str:
    return f"[{title} | v{version or '?'} | {doc_date or 'n/a'}]"


def _row_label(rows: list[int]) -> str:
    return f"row {rows[0]}" if rows[0] == rows[-1] else f"row {rows[0]}-{rows[-1]}"


def chunk_segments(
    segments: list[dict],
    title: str,
    version: str | None,
    doc_date: str | None,
    size: int = CHUNK_TOKENS,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """Return [{text, page_or_row, chunk_index}] with the context prefix applied."""
    prefix = make_prefix(title, version, doc_date)
    raw: list[tuple[str, str]] = []  # (body, label)

    i = 0
    while i < len(segments):
        seg = segments[i]
        meta = seg.get("metadata", {})
        if meta.get("kind") == "row":
            # collect a run of rows from the same sheet; each row is an atomic unit
            sheet = meta.get("sheet")
            j = i
            while (
                j < len(segments)
                and segments[j].get("metadata", {}).get("kind") == "row"
                and segments[j]["metadata"].get("sheet") == sheet
            ):
                j += 1
            run = segments[i:j]
            units = [r["text"] for r in run]
            rownums = [r["metadata"].get("row", k + 1) for k, r in enumerate(run)]
            for a, b in _merge(units, size - count_tokens(prefix), overlap):
                raw.append(("\n".join(units[a:b]), _row_label(rownums[a:b])))
            i = j
        else:
            units = _split(seg["text"], size - count_tokens(prefix))
            for a, b in _merge(units, size - count_tokens(prefix), overlap):
                raw.append(("\n".join(units[a:b]), seg["page_or_row"]))
            i += 1

    return [
        {"text": f"{prefix} {body}", "page_or_row": label, "chunk_index": k}
        for k, (body, label) in enumerate(raw)
    ]
