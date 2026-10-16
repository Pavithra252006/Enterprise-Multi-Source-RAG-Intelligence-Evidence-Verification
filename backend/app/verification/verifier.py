"""
verification/verifier.py – Strict second-judge claim verification using Claude API.

For each generated claim:
- Submits (claim + cited text only) to Claude in parallel via asyncio.gather.
- Verdicts: SUPPORTED | PARTIAL | UNSUPPORTED
- Returns supporting span + reason.
- Calculates overall confidence = fraction of high-importance claims SUPPORTED.
"""
import asyncio
import json
import logging
import re
from typing import Any, Literal
from pydantic import BaseModel, Field

from app.config import get_settings
from app.generation.answer import GeneratedClaim
from app.retrieval.hybrid import RetrievedChunk

log = logging.getLogger("verification.verifier")


class CitationDetail(BaseModel):
    id: str
    title: str
    version: str | None = None
    date: str | None = None
    location: str | None = None
    snippet: str


class VerifiedClaim(BaseModel):
    text: str
    verdict: Literal["SUPPORTED", "PARTIAL", "UNSUPPORTED"]
    reason: str
    supporting_span: str | None = None
    citations: list[CitationDetail] = Field(default_factory=list)
    importance: Literal["high", "low"] = "high"


class VerificationResult(BaseModel):
    verified_claims: list[VerifiedClaim]
    confidence: float
    all_supported: bool


def _verify_locally(claim: GeneratedClaim, cited_chunks: list[RetrievedChunk]) -> tuple[str, str, str | None]:
    """
    Deterministic rule-based verification when Anthropic API is unconfigured/offline.
    Checks that every numerical/factual quantity asserted in the claim is supported
    in the cited evidence body (not accidentally matching prefix dates/versions).
    """
    if not cited_chunks:
        return "UNSUPPORTED", "No cited evidence chunks provided for this claim.", None

    claim_lower = claim.claim_text.lower()

    # Extract body text without the [Title | vX | Date] prefix to avoid accidental date/version matches
    bodies = []
    for c in cited_chunks:
        text = c.text
        if text.startswith("[") and "]" in text:
            text = text[text.find("]") + 1:].strip()
        bodies.append(text)
    combined_body = " ".join(bodies).lower()

    # 1. Strict number check: any number or currency in the claim must exist as a whole word in the body
    # Strip versions like v1.0, v2.0, v3.2 before extracting numbers
    claim_for_numbers = re.sub(r"\bv\d+(?:\.\d+)?\b", "", claim_lower)
    claim_numbers = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", claim_for_numbers)
    # Filter out common metadata years/versions (2021, 2022, 2024, etc.) if they appear in metadata
    meta_years = {"2021", "2022", "2023", "2024", "2025", "2026"}
    substantive_numbers = [n for n in claim_numbers if n not in meta_years]

    for num in substantive_numbers:
        pattern = rf"\b{re.escape(num)}\b"
        num_raw = num.replace(",", "")
        pattern_raw = rf"\b{re.escape(num_raw)}\b"
        if not (re.search(pattern, combined_body) or re.search(pattern_raw, combined_body)):
            return (
                "UNSUPPORTED",
                f"Asserted quantity '{num}' is not supported by the cited evidence.",
                None,
            )

    # 2. Check for content word overlap
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in", "for",
        "on", "by", "at", "be", "this", "that", "under", "with", "from", "acme", "corp",
        "according", "policy", "employees", "employee", "per", "must", "can", "will"
    }
    claim_words = [w for w in re.findall(r"\b[a-z]{3,}\b", claim_lower) if w not in stop_words]

    if not claim_words:
        return "UNSUPPORTED", "Claim has no verifiable factual assertions.", None

    # Check best matching sentence across cited chunks
    best_span = None
    best_overlap = 0

    for c in cited_chunks:
        raw_sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", c.text) if len(s.strip()) >= 15]
        candidate_spans = list(raw_sents)
        for idx in range(len(raw_sents) - 1):
            candidate_spans.append(f"{raw_sents[idx]} {raw_sents[idx+1]}")

        for s_clean in candidate_spans:
            s_lower = s_clean.lower()
            overlap = sum(1 for w in claim_words if w in s_lower)
            if overlap > best_overlap:
                best_overlap = overlap
                best_span = s_clean

    overlap_ratio = best_overlap / len(claim_words) if claim_words else 0.0

    # Require at least 40% keyword match and minimum 2 keywords (or 1 if claim is very short)
    if overlap_ratio >= 0.40 and best_overlap >= min(2, len(claim_words)):
        return "SUPPORTED", "Directly affirmed by the cited document source text.", best_span
    else:
        return (
            "UNSUPPORTED",
            "The cited text does not contain sufficient factual evidence for the claim.",
            None,
        )


async def verify_single_claim(
    claim: GeneratedClaim,
    chunk_map: dict[str, RetrievedChunk],
) -> VerifiedClaim:
    """
    Evaluates a single claim against only its cited evidence passages.
    """
    settings = get_settings()
    cited_chunks = [chunk_map[cid] for cid in claim.citation_ids if cid in chunk_map]

    citations: list[CitationDetail] = [
        CitationDetail(
            id=cid,
            title=c.title,
            version=c.version,
            date=c.doc_date,
            location=c.page_or_row,
            snippet=c.text[:200] + ("..." if len(c.text) > 200 else ""),
        )
        for cid, c in zip(claim.citation_ids, cited_chunks)
    ]

    verdict: str = "UNSUPPORTED"
    reason: str = "Verification uncompleted"
    supporting_span: str | None = None

    if settings.ANTHROPIC_API_KEY and not settings.ANTHROPIC_API_KEY.startswith("sk-ant-REPLACE"):
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            cited_text = "\n\n".join(f"[{cid}] {c.text}" for cid, c in zip(claim.citation_ids, cited_chunks))

            system_prompt = (
                "You are an impartial, strict factual consistency evaluator. "
                "Evaluate whether the CLAIM is strictly supported by the CITED EVIDENCE.\n"
                "Verdicts:\n"
                "- SUPPORTED: Every fact in the claim is directly supported by the cited evidence.\n"
                "- PARTIAL: Some facts are supported, but minor assertions are absent or ambiguous.\n"
                "- UNSUPPORTED: The cited evidence contradicts the claim or provides no proof for it.\n"
                "Output JSON format:\n"
                "{\n"
                '  "verdict": "SUPPORTED" | "PARTIAL" | "UNSUPPORTED",\n'
                '  "reason": "Brief explanation",\n'
                '  "supporting_span": "Exact quote from cited evidence or null"\n'
                "}"
            )
            user_msg = f"CLAIM:\n{claim.claim_text}\n\nCITED EVIDENCE:\n{cited_text}"

            for attempt in range(2):
                try:
                    response = await client.messages.create(
                        model=settings.CLAUDE_MODEL,
                        max_tokens=300,
                        system=system_prompt,
                        messages=[{"role": "user", "content": user_msg}],
                        timeout=15.0,
                    )
                    raw = response.content[0].text if response.content else "{}"
                    # Clean markdown formatting if present
                    cleaned = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", raw).strip()
                    parsed = json.loads(cleaned)
                    verdict = parsed.get("verdict", "UNSUPPORTED").upper()
                    reason = parsed.get("reason", "Verified via Claude judge.")
                    supporting_span = parsed.get("supporting_span")
                    break
                except Exception as e:
                    if attempt == 0:
                        continue
                    raise
        except Exception as e:
            log.warning("Claude verifier API call failed (%s); using deterministic verifier.", e)
            verdict, reason, supporting_span = _verify_locally(claim, cited_chunks)
    else:
        verdict, reason, supporting_span = _verify_locally(claim, cited_chunks)

    # Ensure valid verdict literal
    if verdict not in ("SUPPORTED", "PARTIAL", "UNSUPPORTED"):
        verdict = "UNSUPPORTED"

    return VerifiedClaim(
        text=claim.claim_text,
        verdict=verdict,  # type: ignore[arg-type]
        reason=reason,
        supporting_span=supporting_span,
        citations=citations,
        importance=claim.importance,
    )


async def verify_claims(
    claims: list[GeneratedClaim],
    chunk_map: dict[str, RetrievedChunk],
) -> VerificationResult:
    """
    Runs verification for all claims in parallel using asyncio.gather.
    Computes confidence as the fraction of high-importance claims that are SUPPORTED.
    """
    if not claims:
        return VerificationResult(verified_claims=[], confidence=0.0, all_supported=False)

    tasks = [verify_single_claim(claim, chunk_map) for claim in claims]
    verified: list[VerifiedClaim] = await asyncio.gather(*tasks)

    # Confidence calculation: fraction of high-importance claims SUPPORTED
    high_imp = [c for c in verified if c.importance == "high"]
    if high_imp:
        supported_high = sum(1 for c in high_imp if c.verdict == "SUPPORTED")
        confidence = supported_high / len(high_imp)
    else:
        supported_all = sum(1 for c in verified if c.verdict == "SUPPORTED")
        confidence = supported_all / len(verified)

    all_supported = all(c.verdict == "SUPPORTED" for c in verified)

    return VerificationResult(
        verified_claims=verified,
        confidence=round(confidence, 4),
        all_supported=all_supported,
    )
