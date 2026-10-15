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
    Checks for exact substring or keyword presence in the cited evidence.
    """
    if not cited_chunks:
        return "UNSUPPORTED", "No cited evidence chunks provided for this claim.", None

    combined_text = " ".join(c.text for c in cited_chunks).lower()
    claim_lower = claim.claim_text.lower()

    # Look for key numeric or policy values
    key_terms = re.findall(r"\$?\d+(?:,\d+)*(?:\.\d+)?|\b(?:remote|days|travel|headcount|salary|bonus|vesting)\b", claim_lower)
    matching_terms = [t for t in key_terms if t in combined_text]

    if len(matching_terms) >= max(1, len(key_terms) // 2):
        # Locate a span
        span = None
        for c in cited_chunks:
            for sentence in c.text.split("."):
                if any(t in sentence.lower() for t in key_terms):
                    span = sentence.strip()
                    break
            if span:
                break
        return "SUPPORTED", "Directly affirmed by the cited document source text.", span
    else:
        return "UNSUPPORTED", "The cited text does not contain sufficient factual evidence for the claim.", None


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
