from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parents[3]
SRC_DIR = TESTS_DIR.parent / "src"
sys.path.extend(
    [
        str(SRC_DIR),
        str(REPO_ROOT),
        str(REPO_ROOT / "packages"),
        str(REPO_ROOT / "agents" / "runtime"),
    ]
)

from financial_management_agent import FinancialManagementAgent
from financial_models import DataFactoryPipelineManager, ExchangeRateProvider, TaxRateProvider
from financial_utils import calculate_irr, calculate_npv, calculate_payback_period


class DummyEventBus:
    def __init__(self) -> None:
        self.published: list[tuple[str, dict]] = []

    async def publish(self, topic: str, payload: dict) -> None:
        self.published.append((topic, payload))


def _make_agent(tmp_path: Path) -> FinancialManagementAgent:
    return FinancialManagementAgent(
        config={
            "event_bus": DummyEventBus(),
            "budget_store_path": str(tmp_path / "budgets.json"),
            "actuals_store_path": str(tmp_path / "actuals.json"),
            "forecast_store_path": str(tmp_path / "forecasts.json"),
            "approval_agent_enabled": False,
            "exchange_rate_fixture": str(tmp_path / "rates.json"),
            "tax_rate_fixture": str(tmp_path / "taxes.json"),
        }
    )


def _write_exchange_fixture(tmp_path: Path) -> Path:
    fixture = {
        "base": "AUD",
        "rates": {"AUD": 1.0, "USD": 0.65, "EUR": 0.60},
        "as_of": "2026-01-01T00:00:00+00:00",
    }
    path = tmp_path / "rates.json"
    path.write_text(json.dumps(fixture))
    return path


def _write_tax_fixture(tmp_path: Path) -> Path:
    fixture = {
        "default_rate": 0.10,
        "default_region": "AU",
        "rates": {"AU": 0.10, "US": 0.08},
        "as_of": "2026-01-01T00:00:00+00:00",
    }
    path = tmp_path / "taxes.json"
    path.write_text(json.dumps(fixture))
    return path


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------


def test_calculate_npv_with_positive_cash_flows() -> None:
    """NPV with positive cash flows should exceed zero for a profitable project."""
    total_cost = 1000.0
    cash_flows = [400.0, 400.0, 400.0]
    result = calculate_npv(total_cost, cash_flows, discount_rate=0.10)
    assert result > 0, "Expected positive NPV for cash flows exceeding cost"


def test_calculate_irr_returns_positive_rate() -> None:
    """IRR for a profitable investment should be positive."""
    total_cost = 1000.0
    cash_flows = [400.0, 400.0, 400.0]
    result = calculate_irr(total_cost, cash_flows)
    assert result > 0.0, "Expected positive IRR"


def test_calculate_payback_period() -> None:
    """Payback period should return 2 when cumulative cash flows recover cost in period 2."""
    total_cost = 700.0
    cash_flows = [400.0, 400.0, 400.0]
    result = calculate_payback_period(total_cost, cash_flows)
    assert result == 2, f"Expected payback period 2, got {result}"


def test_calculate_payback_period_not_recovered() -> None:
    """Payback period should return 999 when cost is never recovered."""
    total_cost = 10_000.0
    cash_flows = [100.0, 100.0]
    result = calculate_payback_period(total_cost, cash_flows)
    assert result == 999


# ---------------------------------------------------------------------------
# ExchangeRateProvider tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_exchange_rate_provider_loads_fixture(tmp_path: Path) -> None:
    """ExchangeRateProvider should load and cache rates from a fixture file."""
    fixture_path = _write_exchange_fixture(tmp_path)
    provider = ExchangeRateProvider(fixture_path=fixture_path, ttl_seconds=3600, api_url=None)
    rates = await provider.get_rates()
    assert rates["base"] == "AUD"
    assert "USD" in rates["rates"]
    assert rates["rates"]["USD"] == pytest.approx(0.65)


@pytest.mark.anyio
async def test_exchange_rate_provider_uses_cache(tmp_path: Path) -> None:
    """ExchangeRateProvider should return cached data on second call."""
    fixture_path = _write_exchange_fixture(tmp_path)
    provider = ExchangeRateProvider(fixture_path=fixture_path, ttl_seconds=3600, api_url=None)
    rates_first = await provider.get_rates()
    # Overwrite the fixture - cache should be used
    fixture_path.write_text(json.dumps({"base": "USD", "rates": {}, "as_of": "2020-01-01"}))
    rates_second = await provider.get_rates()
    assert rates_second["base"] == rates_first["base"]


# ---------------------------------------------------------------------------
# TaxRateProvider tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_tax_rate_provider_loads_fixture(tmp_path: Path) -> None:
    """TaxRateProvider should load rates from a fixture file."""
    fixture_path = _write_tax_fixture(tmp_path)
    provider = TaxRateProvider(fixture_path=fixture_path, ttl_seconds=3600, api_url=None)
    rates = await provider.get_rates()
    assert rates["default_region"] == "AU"
    assert rates["rates"]["AU"] == pytest.approx(0.10)


# ---------------------------------------------------------------------------
# DataFactoryPipelineManager tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_data_factory_pipeline_manager_no_client() -> None:
    """Without a real client, schedule_pipeline should return a synthetic run ID."""
    manager = DataFactoryPipelineManager(data_factory_client=None)
    run_id = await manager.schedule_pipeline("my-pipeline", {"param": "value"})
    assert run_id.startswith("run-my-pipeline-")


# ---------------------------------------------------------------------------
# FinancialManagementAgent construction tests
# ---------------------------------------------------------------------------


def test_agent_instantiation(tmp_path: Path) -> None:
    """Agent should instantiate with minimal config without raising."""
    agent = _make_agent(tmp_path)
    assert agent.agent_id == "financial-management-agent"
    assert agent.default_currency == "AUD"


def test_get_capabilities_includes_budget_creation(tmp_path: Path) -> None:
    """get_capabilities should include 'budget_creation'."""
    agent = _make_agent(tmp_path)
    caps = agent.get_capabilities()
    assert "budget_creation" in caps
    assert "financial_forecasting" in caps
    assert "earned_value_management" in caps


# ---------------------------------------------------------------------------
# validate_input tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_validate_input_rejects_missing_action(tmp_path: Path) -> None:
    """validate_input should return False when action is absent."""
    agent = _make_agent(tmp_path)
    result = await agent.validate_input({})
    assert result is False


@pytest.mark.anyio
async def test_validate_input_rejects_create_budget_without_required_fields(
    tmp_path: Path,
) -> None:
    """validate_input should return False when budget fields are missing."""
    agent = _make_agent(tmp_path)
    result = await agent.validate_input(
        {
            "action": "create_budget",
            "budget": {"project_id": "p1"},  # missing total_amount and cost_breakdown
        }
    )
    assert result is False


@pytest.mark.anyio
async def test_validate_input_accepts_valid_create_budget(tmp_path: Path) -> None:
    """validate_input should return True for a complete create_budget payload."""
    agent = _make_agent(tmp_path)
    result = await agent.validate_input(
        {
            "action": "create_budget",
            "budget": {
                "project_id": "p1",
                "total_amount": 100_000,
                "cost_breakdown": {"labor": 100_000},
            },
        }
    )
    assert result is True


@pytest.mark.anyio
async def test_validate_input_rejects_generate_financial_variants_no_scenarios(
    tmp_path: Path,
) -> None:
    """validate_input should return False when scenarios list is missing."""
    agent = _make_agent(tmp_path)
    result = await agent.validate_input(
        {"action": "generate_financial_variants", "project_id": "p1"}
    )
    assert result is False


# ---------------------------------------------------------------------------
# create_budget via process() tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_create_budget_returns_budget_id(tmp_path: Path) -> None:
    """process(create_budget) should return a budget_id with status=Draft."""
    _write_exchange_fixture(tmp_path)
    _write_tax_fixture(tmp_path)
    agent = _make_agent(tmp_path)

    result = await agent.process(
        {
            "action": "create_budget",
            "budget": {
                "project_id": "proj-001",
                "total_amount": 50_000,
                "cost_breakdown": {"labor": 30_000, "overhead": 20_000},
            },
            "context": {"tenant_id": "tenant-test", "user_id": "user-1"},
        }
    )

    assert "budget_id" in result
    assert result["budget_id"].startswith("BDG-")
    assert result["status"] == "Draft"
    assert result["total_amount"] == 50_000


# ---------------------------------------------------------------------------
# generate_financial_variants via process() tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_financial_variants_scenario_comparison(tmp_path: Path) -> None:
    """generate_financial_variants should return scenario metrics for each input scenario."""
    _write_exchange_fixture(tmp_path)
    _write_tax_fixture(tmp_path)
    agent = _make_agent(tmp_path)

    # Seed a budget so the summary has a baseline
    agent.budgets["b1"] = {
        "budget_id": "b1",
        "project_id": "proj-variants",
        "total_amount": 100_000,
        "currency": "AUD",
        "status": "Approved",
        "cost_breakdown": {},
    }

    result = await agent.process(
        {
            "action": "generate_financial_variants",
            "project_id": "proj-variants",
            "scenarios": [
                {"name": "Optimistic", "params": {"budget_delta": -10_000}},
                {"name": "Pessimistic", "params": {"budget_delta": 20_000}},
            ],
            "context": {"tenant_id": "tenant-test"},
        }
    )

    assert result["project_id"] == "proj-variants"
    assert len(result["scenarios"]) == 2
    names = [s["name"] for s in result["scenarios"]]
    assert "Optimistic" in names
    assert "Pessimistic" in names
    summary = result["forecast_summary"]
    assert "best_case" in summary
    assert "worst_case" in summary
