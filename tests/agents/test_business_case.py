import pytest

from business_case_investment_agent import BusinessCaseInvestmentAgent


class EventCollector:
    async def publish(self, topic: str, payload: dict) -> None:
        return None


@pytest.mark.asyncio
async def test_business_case_manual_financial_calculations() -> None:
    agent = BusinessCaseInvestmentAgent(config={"discount_rate": 0.1, "event_bus": EventCollector()})
    await agent.initialize()

    response = await agent.process(
        {
            "action": "calculate_roi",
            "costs": {"total_cost": 1400, "cash_flow": [1000, 200, 200]},
            "benefits": {"total_benefits": 2300, "cash_flow": [500, 900, 900]},
        }
    )

    expected_npv = (500 - 1000) / 1.1 + (900 - 200) / (1.1**2) + (900 - 200) / (1.1**3)
    assert response["npv"] == pytest.approx(expected_npv, abs=0.01)
    assert 0.0 <= response["irr"] <= 1.0
    assert response["payback_period_months"] == 24


@pytest.mark.asyncio
async def test_business_case_scenario_modelling_selects_best_npv() -> None:
    agent = BusinessCaseInvestmentAgent(config={"discount_rate": 0.1, "event_bus": EventCollector()})
    await agent.initialize()

    response = await agent.process(
        {
            "action": "run_scenario_analysis",
            "business_case_id": "BC-1",
            "scenarios": [
                {
                    "name": "base",
                    "parameters": {
                        "base_cost": 1000,
                        "base_benefit": 1400,
                        "cost_multiplier": 1.0,
                        "benefit_multiplier": 1.0,
                    },
                },
                {
                    "name": "optimistic",
                    "parameters": {
                        "base_cost": 1000,
                        "base_benefit": 1700,
                        "cost_multiplier": 0.95,
                        "benefit_multiplier": 1.1,
                    },
                },
            ],
        }
    )

    assert len(response["scenarios"]) == 2
    assert response["recommendation"] == "optimistic"
    assert response["scenarios"][0]["metrics"].keys() >= {
        "npv",
        "irr",
        "payback_period_months",
        "roi_percentage",
    }
