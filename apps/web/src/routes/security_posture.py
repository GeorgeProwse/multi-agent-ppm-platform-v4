"""Enterprise security posture dashboard API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(tags=["security-posture"])


class SecurityPosture(BaseModel):
    posture_score: int  # 0-100
    policy_count: int
    abac_coverage_pct: float
    mfa_enabled_pct: float
    secrets_rotation_status: str  # current, overdue, na
    recent_violations: int
    compliance_checks: list[dict[str, Any]]
    classification_distribution: dict[str, int]


class PolicyDefinition(BaseModel):
    policy_id: str
    name: str
    description: str
    effect: str  # allow, deny
    subjects: dict[str, Any] = Field(default_factory=dict)
    resources: dict[str, Any] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)
    conditions: list[dict[str, Any]] = Field(default_factory=list)
    enabled: bool = True


class PolicyTestRequest(BaseModel):
    policy: PolicyDefinition
    context: dict[str, Any]


class PolicyTestResult(BaseModel):
    decision: str  # allow, deny
    matched_conditions: list[str]
    explanation: str


class ClassifyEntityRequest(BaseModel):
    entity_type: str
    entity_id: str
    classification: str  # public, internal, confidential, restricted


_DEMO_POLICIES: list[PolicyDefinition] = [
    PolicyDefinition(
        policy_id="pol-geo-restrict",
        name="Geo Restriction",
        description="Restrict data access based on user region vs data residency",
        effect="deny",
        subjects={"attributes": ["region"]},
        resources={"attributes": ["data_residency"]},
        actions=["read", "export"],
        conditions=[{"field": "subject.region", "operator": "not_in", "value": "resource.data_residency_regions"}],
    ),
    PolicyDefinition(
        policy_id="pol-time-access",
        name="Time-Based Access",
        description="Deny access outside business hours for confidential data",
        effect="deny",
        subjects={"roles": ["analyst", "contributor"]},
        resources={"classification": ["confidential", "restricted"]},
        actions=["read", "write"],
        conditions=[{"field": "request.hour", "operator": "not_between", "value": [8, 18]}],
    ),
    PolicyDefinition(
        policy_id="pol-mfa-escalation",
        name="Sensitivity Escalation",
        description="Require MFA for restricted classification access",
        effect="deny",
        subjects={"attributes": ["mfa_verified"]},
        resources={"classification": ["restricted"]},
        actions=["read", "write", "delete", "export"],
        conditions=[{"field": "subject.mfa_verified", "operator": "equals", "value": False}],
    ),
    PolicyDefinition(
        policy_id="pol-export-control",
        name="Export Control",
        description="Block data export for confidential and above",
        effect="deny",
        subjects={"roles": ["*"]},
        resources={"classification": ["confidential", "restricted"]},
        actions=["export"],
        conditions=[],
    ),
    PolicyDefinition(
        policy_id="pol-cross-project",
        name="Cross-Project Isolation",
        description="Deny access to projects outside user's assigned portfolio",
        effect="deny",
        subjects={"attributes": ["assigned_portfolio"]},
        resources={"attributes": ["portfolio_id"]},
        actions=["read", "write"],
        conditions=[{"field": "subject.assigned_portfolio", "operator": "not_contains", "value": "resource.portfolio_id"}],
    ),
    PolicyDefinition(
        policy_id="pol-contractor-limit",
        name="Contractor Time Limit",
        description="Deny contractor access after contract end date",
        effect="deny",
        subjects={"attributes": ["employment_type", "contract_end_date"]},
        resources={"types": ["*"]},
        actions=["read", "write"],
        conditions=[{"field": "subject.employment_type", "operator": "equals", "value": "contractor"}, {"field": "current_date", "operator": "gt", "value": "subject.contract_end_date"}],
    ),
]


@router.get("/api/security/posture")
async def security_posture(
    tenant_id: str = Query(default="default"),
) -> SecurityPosture:
    return SecurityPosture(
        posture_score=82,
        policy_count=len(_DEMO_POLICIES) + 2,
        abac_coverage_pct=87.5,
        mfa_enabled_pct=94.0,
        secrets_rotation_status="current",
        recent_violations=3,
        compliance_checks=[
            {"framework": "SOC 2", "status": "pass", "last_audit": "2026-01-15"},
            {"framework": "GDPR", "status": "pass", "last_audit": "2026-02-01"},
            {"framework": "ISO 27001", "status": "partial", "last_audit": "2025-11-30"},
            {"framework": "HIPAA", "status": "na", "last_audit": None},
        ],
        classification_distribution={
            "public": 234,
            "internal": 1856,
            "confidential": 445,
            "restricted": 67,
        },
    )


@router.get("/api/security/policies")
async def list_policies() -> list[PolicyDefinition]:
    return _DEMO_POLICIES


@router.post("/api/security/policies")
async def create_or_update_policy(policy: PolicyDefinition) -> PolicyDefinition:
    for i, existing in enumerate(_DEMO_POLICIES):
        if existing.policy_id == policy.policy_id:
            _DEMO_POLICIES[i] = policy
            return policy
    _DEMO_POLICIES.append(policy)
    return policy


@router.post("/api/security/policies/test")
async def test_policy(request: PolicyTestRequest) -> PolicyTestResult:
    matched: list[str] = []
    for cond in request.policy.conditions:
        matched.append(f"{cond.get('field')} {cond.get('operator')} {cond.get('value')}")
    return PolicyTestResult(
        decision=request.policy.effect,
        matched_conditions=matched,
        explanation=f"Policy '{request.policy.name}' evaluated to {request.policy.effect}. {len(matched)} condition(s) matched.",
    )


@router.get("/api/security/classification-stats")
async def classification_stats(
    tenant_id: str = Query(default="default"),
) -> dict[str, int]:
    return {"public": 234, "internal": 1856, "confidential": 445, "restricted": 67}


@router.post("/api/security/classify-entity")
async def classify_entity(request: ClassifyEntityRequest) -> dict[str, str]:
    return {
        "entity_type": request.entity_type,
        "entity_id": request.entity_id,
        "classification": request.classification,
        "status": "applied",
    }
