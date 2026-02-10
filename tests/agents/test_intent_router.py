import pytest

from intent_router_agent import IntentRouterAgent


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_intent,expected_agent,min_confidence",
    [
        (
            "Show project Apollo budget in USD and ROI",
            "financial_query",
            "financial-management",
            0.8,
        ),
        (
            "What are the top risks for project Atlas?",
            "risk_query",
            "risk-management",
            0.7,
        ),
        (
            "Show schedule milestones for project Borealis",
            "schedule_query",
            "schedule-planning",
            0.6,
        ),
    ],
)
async def test_intent_router_classification_matrix(
    query: str, expected_intent: str, expected_agent: str, min_confidence: float
) -> None:
    agent = IntentRouterAgent(config={"routing_config_path": "ops/config/agents/intent-routing.yaml"})
    await agent.initialize()

    response = await agent.process({"query": query})

    assert response["intents"][0]["intent"] == expected_intent
    assert response["intents"][0]["confidence"] >= min_confidence
    assert any(route["agent_id"] == expected_agent for route in response["routing"])


@pytest.mark.asyncio
async def test_intent_router_extracts_expected_parameters() -> None:
    agent = IntentRouterAgent(config={"routing_config_path": "ops/config/agents/intent-routing.yaml"})
    await agent.initialize()

    response = await agent.process(
        {"query": "Show critical path for project Apollo with a $2.5m USD budget"}
    )

    assert response["parameters"]["project_id"] == "APOLLO"
    assert response["parameters"]["currency"] == "USD"
    assert response["parameters"]["amount"] == 2_500_000
    assert response["parameters"]["schedule_focus"] == "critical_path"
