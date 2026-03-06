"""Executive briefing generator API routes."""

from __future__ import annotations

import time
import uuid
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["briefings"])

_AUDIENCE_PROMPTS = {
    "board": "Focus on strategic alignment, portfolio ROI, and high-level risk posture.",
    "c_suite": "Emphasize financial metrics, budget variance, and business value delivery.",
    "pmo": "Provide operational detail: schedule adherence, resource utilization, governance compliance.",
    "delivery_team": "Tactical focus: sprint progress, blockers, upcoming milestones, team capacity.",
}

_DEMO_BRIEFINGS: list[dict[str, Any]] = []


class BriefingRequest(BaseModel):
    portfolio_id: str = "default"
    audience: str = "c_suite"  # board, c_suite, pmo, delivery_team
    tone: str = "formal"  # formal, concise, detailed
    sections: list[str] = Field(default_factory=lambda: ["highlights", "risks", "financials", "schedule", "resources", "recommendations"])
    format: str = "markdown"  # markdown, html


class BriefingResponse(BaseModel):
    briefing_id: str
    title: str
    generated_at: str
    audience: str
    content: str
    sections: list[dict[str, str]]
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post("/api/briefings/generate")
async def generate_briefing(request: BriefingRequest) -> BriefingResponse:
    """Generate an AI-powered executive briefing."""
    briefing_id = f"brief-{uuid.uuid4().hex[:8]}"
    generated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    audience_label = {
        "board": "Board of Directors",
        "c_suite": "C-Suite Executive",
        "pmo": "PMO Leadership",
        "delivery_team": "Delivery Team",
    }.get(request.audience, "Executive")

    sections: list[dict[str, str]] = []
    content_parts: list[str] = []
    content_parts.append(f"# Portfolio Briefing — {audience_label}\n")
    content_parts.append(f"*Generated: {generated_at} | Portfolio: {request.portfolio_id}*\n")

    if "highlights" in request.sections:
        text = "## Key Highlights\n\n- Portfolio health score: **78/100** (stable)\n- 4 of 6 projects on track for Q2 delivery\n- New demand intake volume up 15% MoM\n- Risk mitigation actions reduced critical risks from 5 to 2\n"
        sections.append({"title": "Key Highlights", "content": text})
        content_parts.append(text)

    if "risks" in request.sections:
        text = "## Risk Summary\n\n| Risk | Severity | Trend | Mitigation |\n|------|----------|-------|------------|\n| Vendor delivery delay (SAP integration) | High | Worsening | Escalated to VP Engineering |\n| Resource shortage — React developers | Medium | Stable | Contractor onboarding initiated |\n| Regulatory compliance gap (GDPR) | Low | Improving | Audit remediation 85% complete |\n"
        sections.append({"title": "Risk Summary", "content": text})
        content_parts.append(text)

    if "financials" in request.sections:
        text = "## Financial Overview\n\n- **Total Budget:** $4.2M | **Spent:** $2.1M (50%)\n- **Forecast at Completion:** $4.35M (+3.6% variance)\n- **Cost Performance Index:** 0.97\n- **Earned Value:** $2.05M\n"
        sections.append({"title": "Financial Overview", "content": text})
        content_parts.append(text)

    if "schedule" in request.sections:
        text = "## Schedule Status\n\n- **Schedule Performance Index:** 0.94\n- **Critical Path:** Data migration → Integration testing → UAT\n- **Next Major Milestone:** Phase 2 Go-Live (2026-04-15)\n- **At-Risk Milestones:** SAP connector deployment (2 weeks behind)\n"
        sections.append({"title": "Schedule Status", "content": text})
        content_parts.append(text)

    if "resources" in request.sections:
        text = "## Resource Utilization\n\n- **Average Utilization:** 87%\n- **Bottleneck Areas:** Python backend (95%), React frontend (92%)\n- **Available Capacity:** DevOps (30%), QA (25%)\n- **Planned Hires:** 3 contractors (starting April)\n"
        sections.append({"title": "Resource Utilization", "content": text})
        content_parts.append(text)

    if "recommendations" in request.sections:
        text = "## AI Recommendations\n\n1. **Accelerate SAP integration** — Assign additional backend developer to reduce critical path by 1 week\n2. **De-scope non-essential Phase 2 features** — Move 3 low-priority items to Phase 3 to protect timeline\n3. **Initiate vendor escalation** — Schedule executive review with SAP account team\n"
        sections.append({"title": "AI Recommendations", "content": text})
        content_parts.append(text)

    content = "\n".join(content_parts)

    briefing = BriefingResponse(
        briefing_id=briefing_id,
        title=f"Portfolio Briefing — {audience_label}",
        generated_at=generated_at,
        audience=request.audience,
        content=content,
        sections=sections,
        metadata={
            "portfolio_id": request.portfolio_id,
            "tone": request.tone,
            "format": request.format,
            "agent_prompt": _AUDIENCE_PROMPTS.get(request.audience, ""),
        },
    )

    _DEMO_BRIEFINGS.append(briefing.model_dump())
    return briefing


@router.get("/api/briefings/history")
async def briefing_history() -> list[dict[str, Any]]:
    return _DEMO_BRIEFINGS[-20:]
