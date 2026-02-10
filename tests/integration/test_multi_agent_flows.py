import pytest

from intent_router_agent import IntentRouterAgent
from response_orchestration_agent import ResponseOrchestrationAgent




class EventCollector:
    async def publish(self, topic: str, payload: dict) -> None:
        return None

class FakeAgent:
    def __init__(self, *, output: dict) -> None:
        self.output = output
        self.calls: list[dict] = []

    async def execute(self, payload: dict) -> dict:
        self.calls.append(payload)
        return self.output


@pytest.mark.asyncio
async def test_full_query_flow_router_to_orchestration() -> None:
    intent_router = IntentRouterAgent(config={"routing_config_path": "ops/config/agents/intent-routing.yaml"})
    await intent_router.initialize()

    financial_agent = FakeAgent(output={"status": "ok", "budget_variance": 0.07})
    risk_agent = FakeAgent(output={"status": "ok", "top_risk": "supplier delay"})
    orchestrator = ResponseOrchestrationAgent(
        config={
            "event_bus": EventCollector(),
            "agent_registry": {
                "financial-management": financial_agent,
                "risk-management": risk_agent,
            }
        }
    )
    await orchestrator.initialize()

    routed = await intent_router.process(
        {"query": "Show budget variance and top risks for project Apollo"}
    )

    response = await orchestrator.process(
        {
            "routing": routed["routing"],
            "parameters": routed["parameters"],
            "query": routed["query"],
            "context": {"tenant_id": "tenant-a", "correlation_id": "corr-1"},
        }
    )
    payload = response.model_dump()

    assert payload["execution_summary"]["successful"] == 2
    assert payload["execution_summary"]["failed"] == 0
    assert "financial-management" in payload["aggregated_response"]
    assert "risk-management" in payload["aggregated_response"]
    assert financial_agent.calls and risk_agent.calls
