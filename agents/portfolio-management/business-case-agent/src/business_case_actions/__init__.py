"""
Business Case Actions Package

Exports all action handlers for the BusinessCaseInvestmentAgent.
"""

from __future__ import annotations

from business_case_actions.analysis_actions import compare_to_historical, generate_recommendation
from business_case_actions.generation_actions import generate_business_case
from business_case_actions.query_actions import get_business_case
from business_case_actions.roi_actions import calculate_roi, run_scenario_analysis

__all__ = [
    "generate_business_case",
    "calculate_roi",
    "run_scenario_analysis",
    "compare_to_historical",
    "generate_recommendation",
    "get_business_case",
]
