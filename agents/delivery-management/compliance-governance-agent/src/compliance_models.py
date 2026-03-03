"""
Compliance & Regulatory Agent - Data Models

Dataclass definitions and the rule engine used across the compliance agent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RegulatoryFramework:
    framework_id: str
    name: str
    description: str
    jurisdiction: list[str]
    industry: list[str]
    data_sensitivity: list[str] = field(default_factory=list)
    effective_date: str | None = None
    applicability_rules: dict[str, Any] = field(default_factory=dict)


@dataclass
class ControlRequirement:
    control_id: str
    regulation_id: str
    description: str
    owner: str
    control_type: str = "preventive"
    requirements: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    test_frequency: str = "quarterly"


@dataclass
class EvidenceSnapshot:
    snapshot_id: str
    project_id: str
    collected_at: str
    sources: list[str]
    metadata: dict[str, Any]
    payload: dict[str, Any]


class ComplianceRuleEngine:
    """Simple rules engine to evaluate compliance evidence against control requirements."""

    def evaluate(self, control: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        requirements = control.get("requirements", [])
        if not requirements:
            requirements = ["implemented", "evidence", "tested"]

        score = 0.0
        max_score = float(len(requirements))
        gaps: list[str] = []

        requirement_checks = {
            "implemented": evidence.get("implementation_status") == "Implemented",
            "evidence": evidence.get("evidence_uploaded", False),
            "tested": evidence.get("recently_tested", False),
            "audit_logs": bool(evidence.get("audit_logs")),
            "risk_mitigation": bool(evidence.get("risk_mitigations")),
            "quality_tests": bool(evidence.get("quality_results")),
            "deployment_checks": bool(evidence.get("deployment_evidence")),
            "data_privacy": evidence.get("privacy_impact_assessed", False),
            "security_scans": bool(evidence.get("security_scans")),
        }

        for requirement in requirements:
            passed = requirement_checks.get(requirement, False)
            if passed:
                score += 1
            else:
                gaps.append(requirement)

        compliance_score = (score / max_score * 100) if max_score else 0.0
        return {
            "score": compliance_score,
            "gaps": gaps,
            "met": compliance_score >= 90,
        }
