"""Natural language to workflow definition parser."""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger("workflow.nl_workflow")

NL_SYSTEM_PROMPT = """You are a workflow definition generator for a Project Portfolio Management system.
Convert the user's natural language description into a structured workflow definition.

Output valid JSON with this schema:
{
  "name": "string",
  "description": "string",
  "steps": [
    {
      "id": "string",
      "type": "task|decision|approval|notification|parallel|api",
      "name": "string",
      "description": "string",
      "agent_id": "string (optional - the agent to handle this step)",
      "config": {},
      "transitions": [
        {"target": "step_id", "condition": "string (optional)"}
      ]
    }
  ]
}

Available step types:
- task: An action performed by an agent or user
- decision: A branching point with conditional transitions
- approval: Requires human approval before proceeding
- notification: Send a notification to stakeholders
- parallel: Execute multiple sub-steps concurrently
- api: Call an external API

Available agents: intent-router, demand-intake, business-case, portfolio-optimisation,
program-management, scope-definition, lifecycle-governance, schedule-planning,
resource-management, financial-management, vendor-procurement, quality-management,
risk-management, compliance-governance, change-control, release-deployment,
knowledge-management, continuous-improvement, stakeholder-communications,
analytics-insights, data-synchronisation, system-health, workflow-engine.

Return ONLY the JSON, no markdown formatting."""

REFINE_PROMPT = """The user wants to modify this existing workflow definition.
Current definition:
{current_definition}

User feedback: {feedback}

Output the updated workflow definition as valid JSON. Return ONLY the JSON."""


class NLWorkflowParser:
    """Parse natural language descriptions into workflow definitions."""

    def parse(self, description: str) -> dict[str, Any]:
        """Convert a natural language description to a workflow definition.

        In production this calls LLMRouter; here we return a representative
        demo definition to showcase the feature without requiring live LLM access.
        """
        return {
            "name": "Generated Workflow",
            "description": description,
            "steps": [
                {
                    "id": "step-1",
                    "type": "task",
                    "name": "Intake & Classification",
                    "description": "Receive and classify the incoming request",
                    "agent_id": "demand-intake",
                    "config": {},
                    "transitions": [{"target": "step-2"}],
                },
                {
                    "id": "step-2",
                    "type": "decision",
                    "name": "Risk Assessment Gate",
                    "description": "Evaluate risk level of the request",
                    "agent_id": "risk-management",
                    "config": {},
                    "transitions": [
                        {"target": "step-3", "condition": "risk_level == 'high'"},
                        {"target": "step-4", "condition": "risk_level != 'high'"},
                    ],
                },
                {
                    "id": "step-3",
                    "type": "approval",
                    "name": "Executive Approval",
                    "description": "High-risk items require executive sign-off",
                    "config": {"approver_role": "executive"},
                    "transitions": [{"target": "step-4"}],
                },
                {
                    "id": "step-4",
                    "type": "task",
                    "name": "Execute & Deliver",
                    "description": "Execute the planned work",
                    "agent_id": "schedule-planning",
                    "config": {},
                    "transitions": [{"target": "step-5"}],
                },
                {
                    "id": "step-5",
                    "type": "notification",
                    "name": "Stakeholder Update",
                    "description": "Notify stakeholders of completion",
                    "agent_id": "stakeholder-communications",
                    "config": {},
                    "transitions": [],
                },
            ],
        }

    def validate_generated(self, definition: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        if not definition.get("name"):
            errors.append("Workflow must have a name")
        steps = definition.get("steps", [])
        if not steps:
            errors.append("Workflow must have at least one step")
        step_ids = {s.get("id") for s in steps}
        for step in steps:
            for t in step.get("transitions", []):
                if t.get("target") and t["target"] not in step_ids:
                    errors.append(f"Step {step.get('id')} references unknown target {t['target']}")
        return {"valid": len(errors) == 0, "errors": errors}

    def refine(self, definition: dict[str, Any], feedback: str) -> dict[str, Any]:
        """Refine an existing definition based on user feedback.

        In production this calls LLM with REFINE_PROMPT; here returns original unchanged.
        """
        return definition
