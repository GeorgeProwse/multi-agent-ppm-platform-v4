"""
Resource & Capacity Management Agent - Action Handlers

Each module contains action handler functions that implement specific
agent capabilities. They are called from the main ResourceCapacityAgent.process() method.
"""

from actions.allocation import allocate_resource
from actions.availability import get_availability
from actions.capacity_planning import forecast_capacity, plan_capacity
from actions.conflicts import identify_conflicts
from actions.demand_management import approve_request, request_resource
from actions.resource_pool import add_resource, delete_resource, get_resource_pool, update_resource
from actions.scenario_analysis import scenario_analysis
from actions.search_and_match import match_skills, search_resources
from actions.utilization import get_utilization

__all__ = [
    "add_resource",
    "update_resource",
    "delete_resource",
    "get_resource_pool",
    "request_resource",
    "approve_request",
    "search_resources",
    "match_skills",
    "forecast_capacity",
    "plan_capacity",
    "scenario_analysis",
    "allocate_resource",
    "get_availability",
    "get_utilization",
    "identify_conflicts",
]
