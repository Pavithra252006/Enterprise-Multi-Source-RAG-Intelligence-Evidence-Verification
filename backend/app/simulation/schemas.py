from typing import Literal
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    scenario: str = Field(..., description="Proposed policy change or corporate hypothetical scenario")
    user_id: str = Field(default="executive", description="User clearance identity running the simulation")


class AffectedDoc(BaseModel):
    title: str
    source: str
    version: str | None = None
    doc_date: str | None = None
    access_level: int = 1
    clause_excerpt: str
    impact_level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = "MEDIUM"


class RippleConflict(BaseModel):
    conflict_title: str
    target_doc: str
    conflicting_rule: str
    hypothetical_impact: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = "HIGH"


class OperationalImpact(BaseModel):
    category: str = "Operational"
    metric_delta: str | None = None
    description: str


class Amendment(BaseModel):
    doc_name: str
    section: str
    current_clause: str
    proposed_clause: str
    priority: Literal["Immediate", "High", "Medium"] = "High"


class RoleImpact(BaseModel):
    role: str
    clearance: int
    impact_summary: str


class SimulationResult(BaseModel):
    scenario_title: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    summary: str
    affected_documents: list[AffectedDoc] = Field(default_factory=list)
    ripple_conflicts: list[RippleConflict] = Field(default_factory=list)
    operational_impacts: list[OperationalImpact] = Field(default_factory=list)
    recommended_amendments: list[Amendment] = Field(default_factory=list)
    role_impact_matrix: list[RoleImpact] = Field(default_factory=list)


class PresetScenario(BaseModel):
    id: str
    title: str
    short_desc: str
    category: str
    scenario_text: str
