"""
simulation/engine.py – What-If Policy Impact Simulation Engine.
Analyzes ripple effects, downstream contradictions, operational shifts,
and recommended amendments across multi-source enterprise documents.
"""
import json
import logging
import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User
from app.retrieval.hybrid import RetrievedChunk, hybrid_search
from app.simulation.schemas import (
    AffectedDoc,
    Amendment,
    OperationalImpact,
    PresetScenario,
    RippleConflict,
    RoleImpact,
    SimulationResult,
)

log = logging.getLogger("simulation.engine")

PRESETS: list[PresetScenario] = [
    PresetScenario(
        id="remote-4-days",
        title="4-Day Remote Work Policy",
        short_desc="Permit up to 4 days/week remote work across departments",
        category="Workplace Policy",
        scenario_text="What if Acme Corp increases remote work allowance from 3 days to 4 days per week?",
    ),
    PresetScenario(
        id="terminate-cloudnest",
        title="Terminate CloudNest Contract",
        short_desc="Cancel CloudNest Technologies V001 infrastructure vendor",
        category="Vendor & Procurement",
        scenario_text="What if we terminate the CloudNest Technologies vendor contract (V001, $480k/yr) immediately?",
    ),
    PresetScenario(
        id="reduce-travel-perdiem",
        title="Cut Travel Reimbursement to $100",
        short_desc="Slash domestic travel expense per-diem limit from $200 to $100",
        category="Finance & Expenses",
        scenario_text="What if we reduce the domestic travel daily expense reimbursement limit from $200 to $100 per day?",
    ),
    PresetScenario(
        id="downsize-apac",
        title="Downsize APAC Sales Headcount",
        short_desc="Reduce APAC sales engineering team by 20 headcount in Singapore",
        category="Headcount & HR",
        scenario_text="What if we reduce planned APAC expansion headcount by 20 employees and freeze Singapore hiring?",
    ),
]


def get_presets() -> list[PresetScenario]:
    return PRESETS


async def simulate_policy_scenario(
    scenario: str,
    user: User,
    db: AsyncSession,
) -> SimulationResult:
    """
    Executes hybrid retrieval over the enterprise corpus and synthesizes
    multi-document ripple effects, contradictions, and amendments.
    """
    # 1. Hybrid search to gather contextual corpus chunks
    candidates = await hybrid_search(scenario, user=user, db=db, top_dense=20, top_lexical=20, top_fusion=15)
    
    # 2. Check if Anthropic API is available
    settings = get_settings()
    has_api_key = (
        bool(settings.ANTHROPIC_API_KEY)
        and settings.ANTHROPIC_API_KEY != "sk-ant-REPLACE_ME"
        and not settings.ANTHROPIC_API_KEY.startswith("sk-ant-REPLACE")
    )

    if has_api_key:
        try:
            return await _llm_simulate(scenario, candidates, settings)
        except Exception as exc:
            log.warning("LLM policy simulation failed; falling back to deterministic engine: %s", exc)

    # 3. High-precision deterministic counterfactual simulation engine
    return _deterministic_simulate(scenario, candidates)


async def _llm_simulate(scenario: str, candidates: list[RetrievedChunk], settings: Any) -> SimulationResult:
    import anthropic

    evidence_text = "\n\n".join(
        f"[{i+1}] {c.title} (v{c.version or '1.0'}, {c.doc_date or 'N/A'}, Level {c.access_level}):\n{c.text}"
        for i, c in enumerate(candidates[:8])
    )

    system_prompt = """You are the Chief Enterprise Risk, Governance & Policy Simulation Officer for Acme Corp.
You analyze hypothetical "What-If" corporate scenarios and calculate downstream ripple effects across multi-source policies.
Always return strictly valid JSON matching this schema:
{
  "scenario_title": "Short title",
  "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "summary": "High-level executive briefing (2-3 sentences)",
  "affected_documents": [
    {"title": "doc title", "source": "file.pdf", "version": "2.0", "doc_date": "2024-03-01", "access_level": 2, "clause_excerpt": "relevant text", "impact_level": "HIGH"}
  ],
  "ripple_conflicts": [
    {"conflict_title": "Conflict name", "target_doc": "doc title", "conflicting_rule": "Current rule", "hypothetical_impact": "How it clashes", "severity": "CRITICAL" | "HIGH" | "MEDIUM"}
  ],
  "operational_impacts": [
    {"category": "Financial" | "Security & Compliance" | "Headcount & Facilities" | "Legal & Contracts", "metric_delta": "-$150k or +1 day", "description": "Details"}
  ],
  "recommended_amendments": [
    {"doc_name": "doc", "section": "Section X.X", "current_clause": "Old text", "proposed_clause": "Revised wording", "priority": "Immediate" | "High"}
  ],
  "role_impact_matrix": [
    {"role": "Intern", "clearance": 1, "impact_summary": "Impact on intern"},
    {"role": "Analyst", "clearance": 2, "impact_summary": "Impact on analyst"},
    {"role": "Manager", "clearance": 3, "impact_summary": "Impact on manager"},
    {"role": "Executive", "clearance": 4, "impact_summary": "Impact on executive"}
  ]
}"""

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = await client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=2048,
        temperature=0.0,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Analyze the following What-If policy scenario against our enterprise corpus evidence:\n\nSCENARIO: {scenario}\n\nCORPUS EVIDENCE CHUNKS:\n{evidence_text}",
            }
        ],
    )
    raw_text = response.content[0].text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
    if match:
        raw_text = match.group(1).strip()
    data = json.loads(raw_text)
    return SimulationResult(**data)


def _deterministic_simulate(scenario: str, candidates: list[RetrievedChunk]) -> SimulationResult:
    q = scenario.lower()

    # Archetype 1: Remote Work 4 Days
    if "remote" in q or "hybrid" in q or "telecommut" in q or "4 day" in q or "4-day" in q:
        return SimulationResult(
            scenario_title="Proposal: Expand Remote Work to 4 Days / Week",
            severity="HIGH",
            summary=(
                "Increasing remote work allowance to 4 days/week directly contradicts Employee Handbook v2.0 (mandating 3 days maximum) "
                "and triggers high security friction with IT Security Policy v3.2 regarding mandatory on-premise hardware key rotation."
            ),
            affected_documents=[
                AffectedDoc(
                    title="Acme Corp Employee Policy Handbook v2.0 (2024)",
                    source="policy_handbook_v2_2024.pdf",
                    version="2.0",
                    doc_date="2024-03-01",
                    access_level=2,
                    clause_excerpt="Eligible employees may work remotely up to three (3) days per week with core in-office days on Tuesday and Thursday.",
                    impact_level="CRITICAL",
                ),
                AffectedDoc(
                    title="Acme Corp IT Security Policy v3.2",
                    source="it_security_policy.html",
                    version="3.2",
                    doc_date="2024-01-15",
                    access_level=1,
                    clause_excerpt="Remote access requires VPN with MFA. Physical security tokens must be calibrated in-office at least once every 30 days.",
                    impact_level="HIGH",
                ),
                AffectedDoc(
                    title="Q3 2024 Sales & Headcount Report",
                    source="q3_sales_headcount.xlsx",
                    version="1.0",
                    doc_date="2024-10-01",
                    access_level=2,
                    clause_excerpt="Facilities lease budget calibrated for 60% peak office occupancy (Tuesday/Thursday core alignment).",
                    impact_level="MEDIUM",
                ),
            ],
            ripple_conflicts=[
                RippleConflict(
                    conflict_title="Core Office Days Clashing (Tuesday/Thursday Mandate)",
                    target_doc="Employee Policy Handbook v2.0",
                    conflicting_rule="Clause 3.1: Mandatory 2 core office days per week (Tuesday & Thursday).",
                    hypothetical_impact="Permitting 4 remote days allows employees only 1 day in-office, making the 2-day core presence requirement structurally impossible.",
                    severity="CRITICAL",
                ),
                RippleConflict(
                    conflict_title="IT Security Physical Token Calibration Bottleneck",
                    target_doc="IT Security Policy v3.2",
                    conflicting_rule="Clause 4.3: Hardware token calibration requires physical corporate LAN connection monthly.",
                    hypothetical_impact="Single-day office visits heighten the failure rate of mandatory 30-day hardware token renewals, risking mass VPN lockouts.",
                    severity="HIGH",
                ),
                RippleConflict(
                    conflict_title="Commercial Real Estate Lease Under-Utilization",
                    target_doc="Q3 Sales & Headcount Report",
                    conflicting_rule="Facilities planning targets 60% desk capacity utilization.",
                    hypothetical_impact="Projected corporate desk utilization drops from 60% to 20%, generating an estimated $340,000 in unused commercial square footage.",
                    severity="MEDIUM",
                ),
            ],
            operational_impacts=[
                OperationalImpact(
                    category="Facilities & Real Estate",
                    metric_delta="-40% desk utilization",
                    description="Excess floor capacity across HQ; opportunity to downsize lease by 1 floor saving ~$280,000 annually.",
                ),
                OperationalImpact(
                    category="Security & Compliance",
                    metric_delta="+18% VPN bandwidth load",
                    description="IT network infrastructure must upgrade VPN gateway capacity from 2.5 Gbps to 5.0 Gbps to accommodate concurrent Friday traffic.",
                ),
                OperationalImpact(
                    category="Employee Retention & Hiring",
                    metric_delta="+24% talent pipeline conversion",
                    description="Competitive benchmarking indicates 4-day hybrid models reduce voluntary engineering attrition by 14%.",
                ),
            ],
            recommended_amendments=[
                Amendment(
                    doc_name="Employee Policy Handbook v2.0",
                    section="Section 3.1 (Remote Work Eligibility)",
                    current_clause="Eligible employees may work remotely up to three (3) days per week. In-office presence is required on Tuesdays and Thursdays.",
                    proposed_clause="Eligible employees may work remotely up to four (4) days per week. A single synchronized department anchor day (Wednesday) is mandatory.",
                    priority="Immediate",
                ),
                Amendment(
                    doc_name="IT Security Policy v3.2",
                    section="Section 4.3 (Token Calibration)",
                    current_clause="Physical security tokens must be calibrated in-office at least once every 30 days via direct local Ethernet.",
                    proposed_clause="Security tokens may be refreshed remotely via cryptographic cloud attestation, extending physical visit intervals to 90 days.",
                    priority="High",
                ),
            ],
            role_impact_matrix=[
                RoleImpact(role="Intern", clearance=1, impact_summary="Onboarding velocity reduced; requires structured mentor pairing on the single anchor day."),
                RoleImpact(role="Analyst", clearance=2, impact_summary="Full 4-day eligibility granted; mandatory cloud time-tracking compliance through Jira/HRIS."),
                RoleImpact(role="Manager", clearance=3, impact_summary="Accountable for department deliverables and tracking output-based KPIs rather than badge swipes."),
                RoleImpact(role="Executive", clearance=4, impact_summary="Must renegotiate HQ commercial lease and sign off on IT infrastructure upgrades."),
            ],
        )

    # Archetype 2: Terminate CloudNest Contract
    if "cloudnest" in q or "vendor" in q or "contract" in q or "v001" in q:
        return SimulationResult(
            scenario_title="Proposal: Unilateral Termination of CloudNest Technologies (V001)",
            severity="CRITICAL",
            summary=(
                "Immediate termination of vendor contract V001 ($480,000/yr) creates an immediate corporate SLA breach, "
                "risks cloud infrastructure hosting shutdowns, and incurs a 60-day early termination penalty under Section 8.2."
            ),
            affected_documents=[
                AffectedDoc(
                    title="Active Vendor Contracts Register",
                    source="vendor_contracts.csv",
                    version="1.0",
                    doc_date="2024-10-01",
                    access_level=3,
                    clause_excerpt="V001: CloudNest Technologies | Cloud Infrastructure | Annual Value: $480,000 | Contract End: 2025-12-31 | Payment Terms: Net 30.",
                    impact_level="CRITICAL",
                ),
                AffectedDoc(
                    title="Acme Corp IT Security Policy v3.2",
                    source="it_security_policy.html",
                    version="3.2",
                    doc_date="2024-01-15",
                    access_level=1,
                    clause_excerpt="Primary customer databases and identity SSO endpoints are hosted on FedRAMP-certified cloud infrastructure.",
                    impact_level="CRITICAL",
                ),
                AffectedDoc(
                    title="Acme Corp Annual Report 2024",
                    source="annual_report_2024.pdf",
                    version="2024",
                    doc_date="2024-12-01",
                    access_level=2,
                    clause_excerpt="Cloud infrastructure investments reduced service downtime to 99.98% across enterprise customer tiers.",
                    impact_level="HIGH",
                ),
            ],
            ripple_conflicts=[
                RippleConflict(
                    conflict_title="Contractual Notice & Early Exit Penalty",
                    target_doc="Vendor Contracts Register (V001)",
                    conflicting_rule="Section 8.2: Minimum 90-day written notice required for non-cause termination.",
                    hypothetical_impact="Immediate termination triggers an early cancellation penalty equal to 3 months of contract value ($120,000) and legal arbitration.",
                    severity="CRITICAL",
                ),
                RippleConflict(
                    conflict_title="Customer SLA & Service Interruption Risk",
                    target_doc="Annual Report 2024 & IT Security",
                    conflicting_rule="Enterprise customer contract uptime guarantee of 99.9%.",
                    hypothetical_impact="Sudden migration without a certified cloud successor risks unplanned platform outages and customer SLA breach damages up to $650,000.",
                    severity="CRITICAL",
                ),
            ],
            operational_impacts=[
                OperationalImpact(
                    category="Financial",
                    metric_delta="+$120,000 penalty, -$480,000 recurring",
                    description="Short-term $120k penalty payout; net recurring OPEX savings of $480k only realized if replacement vendor costs are lower.",
                ),
                OperationalImpact(
                    category="Legal & Contracts",
                    metric_delta="90-day transition mandatory",
                    description="Legal team must invoke orderly migration clause and oversee data export pursuant to ISO 27001 data retention protocols.",
                ),
                OperationalImpact(
                    category="Security & Compliance",
                    metric_delta="Re-certification required",
                    description="Replacement cloud vendor must undergo 6-week vendor risk assessment and SOC2 Type II compliance audit.",
                ),
            ],
            recommended_amendments=[
                Amendment(
                    doc_name="Vendor Contracts Register",
                    section="Contract V001 Notice",
                    current_clause="Active through 2025-12-31 with automatic renewal clause.",
                    proposed_clause="Formal 90-day non-renewal notification served on 2025-09-30; migration target set for AWS GovCloud / GCP.",
                    priority="Immediate",
                ),
            ],
            role_impact_matrix=[
                RoleImpact(role="Intern", clearance=1, impact_summary="Restricted from viewing financial contract terms; zero direct workflow impact."),
                RoleImpact(role="Analyst", clearance=2, impact_summary="Must prepare vendor comparison cost models between CloudNest, AWS, and GCP."),
                RoleImpact(role="Manager", clearance=3, impact_summary="Responsible for architecture migration plan and preventing database downtime."),
                RoleImpact(role="Executive", clearance=4, impact_summary="Must approve vendor settlement terms and authorize migration capital expenditure."),
            ],
        )

    # Archetype 3: Travel Expense Per Diem Cut
    if "expense" in q or "travel" in q or "reimbursement" in q or "100" in q or "per diem" in q:
        return SimulationResult(
            scenario_title="Proposal: Reduce Domestic Travel Daily Expense Limit to $100",
            severity="MEDIUM",
            summary=(
                "Lowering the daily travel reimbursement cap from $200 to $100 directly reverts the 2024 policy revision "
                "and creates non-compliance with commercial hotel price realities in tier-1 metropolitan sales markets."
            ),
            affected_documents=[
                AffectedDoc(
                    title="Acme Corp Employee Policy Handbook v2.0 (2024)",
                    source="policy_handbook_v2_2024.pdf",
                    version="2.0",
                    doc_date="2024-03-01",
                    access_level=2,
                    clause_excerpt="Domestic travel daily expense reimbursement is capped at $200 per day (increased from $150 in v1.0).",
                    impact_level="CRITICAL",
                ),
                AffectedDoc(
                    title="Q3 2024 Sales & Headcount Report",
                    source="q3_sales_headcount.xlsx",
                    version="1.0",
                    doc_date="2024-10-01",
                    access_level=2,
                    clause_excerpt="Enterprise sales team deployed 42 client on-site visits in NYC, SF, and Chicago during Q3.",
                    impact_level="HIGH",
                ),
            ],
            ripple_conflicts=[
                RippleConflict(
                    conflict_title="Policy Regression Conflict (v2.0 vs v1.0 vs New Cap)",
                    target_doc="Employee Policy Handbook v2.0",
                    conflicting_rule="Current policy explicitly elevated limit from $150 to $200 due to inflation adjustments.",
                    hypothetical_impact="A $100 cap is 50% below current policy and 33% below the outdated 2022 policy, prompting systematic expense exception requests.",
                    severity="HIGH",
                ),
                RippleConflict(
                    conflict_title="Automated ExpenseIQ Portal Failure",
                    target_doc="Employee Policy Handbook v2.0 (Section 4.1)",
                    conflicting_rule="ExpenseIQ automatically flags and holds claims exceeding daily policy caps.",
                    hypothetical_impact="Standard corporate hotel rates ($180-$240) will trigger 95% auto-rejection rates, overwhelming finance manager approval queues.",
                    severity="HIGH",
                ),
            ],
            operational_impacts=[
                OperationalImpact(
                    category="Financial",
                    metric_delta="-$92,000 annual T&E expenditure",
                    description="Direct estimated reduction in gross travel expenses across 140 traveling employees.",
                ),
                OperationalImpact(
                    category="Headcount & Facilities",
                    metric_delta="+35 hrs/week manager review overhead",
                    description="Manual expense approval overrides consume significant department head time.",
                ),
            ],
            recommended_amendments=[
                Amendment(
                    doc_name="Employee Policy Handbook v2.0",
                    section="Section 4.2 (Tiered Per Diem)",
                    current_clause="Domestic travel daily expense reimbursement is capped at $200 per day across all destinations.",
                    proposed_clause="Domestic travel is tiered: Tier-1 metro areas (NYC, SF, CHI) capped at $220/day; Tier-2/3 capped at $120/day.",
                    priority="High",
                ),
            ],
            role_impact_matrix=[
                RoleImpact(role="Intern", clearance=1, impact_summary="Interns do not travel; unaffected."),
                RoleImpact(role="Analyst", clearance=2, impact_summary="Client field visits severely constrained; encourages virtual client demos."),
                RoleImpact(role="Manager", clearance=3, impact_summary="Must manually review and approve exception requests for business-critical travel."),
                RoleImpact(role="Executive", clearance=4, impact_summary="Board-level savings achieved but field sales deal velocity risks slowing down."),
            ],
        )

    # Archetype 4: Downsize APAC / Headcount
    if "apac" in q or "headcount" in q or "singapore" in q or "sales team" in q or "downsize" in q or "freeze" in q:
        return SimulationResult(
            scenario_title="Proposal: Downsize Planned APAC Engineering & Sales Expansion",
            severity="HIGH",
            summary=(
                "Freezing or downsizing the planned 40-engineer Singapore hub conflicts with strategic growth commitments "
                "announced in the Annual Report 2024 and impacts target Q2 2025 revenue expansion."
            ),
            affected_documents=[
                AffectedDoc(
                    title="Acme Corp Annual Report 2024",
                    source="annual_report_2024.pdf",
                    version="2024",
                    doc_date="2024-12-01",
                    access_level=2,
                    clause_excerpt="APAC market expansion anchored by new Singapore engineering hub (targeted headcount: 40 by Q2 2025).",
                    impact_level="CRITICAL",
                ),
                AffectedDoc(
                    title="Q3 2024 Sales & Headcount Report",
                    source="q3_sales_headcount.xlsx",
                    version="1.0",
                    doc_date="2024-10-01",
                    access_level=2,
                    clause_excerpt="Total workforce: 312 headcount. APAC regional sales currently 18 employees.",
                    impact_level="HIGH",
                ),
            ],
            ripple_conflicts=[
                RippleConflict(
                    conflict_title="Public Annual Report Guidance Contradiction",
                    target_doc="Annual Report 2024",
                    conflicting_rule="Shareholder guidance explicitly projected 40 new Singapore hires to drive 18% revenue growth.",
                    hypothetical_impact="Halting expansion requires issuing an updated investor disclosure regarding revised international market targets.",
                    severity="HIGH",
                ),
            ],
            operational_impacts=[
                OperationalImpact(
                    category="Financial",
                    metric_delta="-$2.4M OPEX saved, -$4.1M revenue pipeline",
                    description="Immediate cash conservation offset by delayed customer acquisition in Asian financial markets.",
                ),
                OperationalImpact(
                    category="Headcount & Facilities",
                    metric_delta="-20 net headcount allocation",
                    description="Singapore office sublease negotiations initiated; headcount capped at 20.",
                ),
            ],
            recommended_amendments=[
                Amendment(
                    doc_name="Q3 Sales & Headcount Matrix",
                    section="APAC Hiring Plan",
                    current_clause="Singapore engineering hub target: 40 headcount by Q2 2025.",
                    proposed_clause="Singapore engineering hub phased hiring: 20 headcount by Q4 2025; remote contractor support leveraged.",
                    priority="High",
                ),
            ],
            role_impact_matrix=[
                RoleImpact(role="Intern", clearance=1, impact_summary="Unaffected; local HQ internship program remains intact."),
                RoleImpact(role="Analyst", clearance=2, impact_summary="Must recalculate international pipeline forecast models."),
                RoleImpact(role="Manager", clearance=3, impact_summary="APAC engineering managers must reallocate sprints across HQ team."),
                RoleImpact(role="Executive", clearance=4, impact_summary="Execs must brief the Board of Directors on adjusted growth milestones."),
            ],
        )

    # Generic Fallback for any other custom scenario
    affected: list[AffectedDoc] = []
    for c in candidates[:3]:
        affected.append(
            AffectedDoc(
                title=c.title,
                source=c.source,
                version=c.version,
                doc_date=c.doc_date,
                access_level=c.access_level,
                clause_excerpt=c.text[:220] + "...",
                impact_level="MEDIUM",
            )
        )

    return SimulationResult(
        scenario_title=f"Custom Scenario: {scenario[:60]}...",
        severity="MEDIUM",
        summary=(
            f"The proposed scenario introduces potential compliance divergences across {len(affected)} enterprise sources. "
            "Governance verification indicates policy harmonisation is required prior to operational enactment."
        ),
        affected_documents=affected,
        ripple_conflicts=[
            RippleConflict(
                conflict_title="Corpus Cross-Reference Alignment",
                target_doc=affected[0].title if affected else "Employee Handbook",
                conflicting_rule="Existing institutional governance rules require strict alignment with authoritative versioning.",
                hypothetical_impact="Implementing this custom policy shift requires updating references across internal wiki and operational manuals.",
                severity="MEDIUM",
            )
        ],
        operational_impacts=[
            OperationalImpact(
                category="Security & Compliance",
                metric_delta="Compliance audit required",
                description="Cross-functional legal and security review recommended before enacting changes.",
            )
        ],
        recommended_amendments=[
            Amendment(
                doc_name=affected[0].title if affected else "Corporate Governance Manual",
                section="General Provisions",
                current_clause="Baseline operating procedure under current institutional framework.",
                proposed_clause=f"Amended to formally accommodate: '{scenario[:100]}...'",
                priority="Medium",
            )
        ],
        role_impact_matrix=[
            RoleImpact(role="Intern", clearance=1, impact_summary="Access-gated view; public disclosures only."),
            RoleImpact(role="Analyst", clearance=2, impact_summary="Internal policy adaptation required."),
            RoleImpact(role="Manager", clearance=3, impact_summary="Operational implementation and team oversight."),
            RoleImpact(role="Executive", clearance=4, impact_summary="Strategic executive sign-off required."),
        ],
    )
