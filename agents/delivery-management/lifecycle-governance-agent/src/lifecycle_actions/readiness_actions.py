"""Action handlers for readiness model training and scoring."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lifecycle_utils import get_lifecycle_state, get_pending_gates

if TYPE_CHECKING:
    from project_lifecycle_agent import ProjectLifecycleAgent


async def train_readiness_model(
    agent: ProjectLifecycleAgent, project_id: str, *, tenant_id: str
) -> dict[str, Any]:
    history = agent.persistence.list_gate_outcomes(tenant_id, project_id)
    if not history:
        return {"status": "skipped", "reason": "no_gate_history"}
    samples = []
    ai_samples = []
    for record in history:
        payload = record["payload"]
        criteria_status = payload.get("criteria_status", [])
        health_snapshot = payload.get("health_snapshot", {})
        features = agent.readiness_model.build_features(criteria_status, health_snapshot)
        label = 1.0 if payload.get("criteria_met") else 0.0
        samples.append({"features": features, "label": label})
        readiness_features = payload.get(
            "readiness_features"
        ) or agent.readiness_model.build_readiness_features(
            agent.projects.get(project_id), health_snapshot, criteria_status
        )
        ai_samples.append({"features": readiness_features, "label": label})
    agent.readiness_model.fit(samples)
    ai_result = agent.readiness_model.train_with_ai_service(agent.ai_model_service, ai_samples)
    return {
        "status": "trained",
        "samples": len(samples),
        "ai_model": ai_result,
    }


async def score_readiness(
    agent: ProjectLifecycleAgent, project_id: str, *, tenant_id: str
) -> dict[str, Any]:
    lifecycle_state = await get_lifecycle_state(agent, tenant_id, project_id)
    if not lifecycle_state:
        raise ValueError(f"Lifecycle state not found for project: {project_id}")
    pending_gates = await get_pending_gates(agent, project_id)
    gate_name = pending_gates[0] if pending_gates else "current_gate"

    from lifecycle_actions.evaluate_gate import evaluate_gate

    evaluation = await evaluate_gate(agent, project_id, gate_name, tenant_id=tenant_id)
    return {
        "project_id": project_id,
        "gate_name": gate_name,
        "readiness_score": evaluation.get("readiness_score"),
        "criteria_met": evaluation.get("criteria_met"),
        "readiness_model": evaluation.get("readiness_model"),
    }
