"""
Action handlers for the Schedule Planning Agent.

Each module contains one or more action handlers that are delegated to
from the main SchedulePlanningAgent.process() method.
"""

from actions.baseline import manage_baseline, track_variance
from actions.create_schedule import create_schedule
from actions.critical_path import calculate_critical_path
from actions.estimate_duration import estimate_duration
from actions.map_dependencies import map_dependencies
from actions.milestones import track_milestones
from actions.monte_carlo import run_monte_carlo
from actions.optimize import optimize_schedule
from actions.resource_scheduling import resource_constrained_schedule
from actions.schedule_crud import get_schedule, update_schedule
from actions.sprint_planning import sprint_planning
from actions.what_if import generate_schedule_variants, what_if_analysis

__all__ = [
    "create_schedule",
    "estimate_duration",
    "map_dependencies",
    "calculate_critical_path",
    "resource_constrained_schedule",
    "run_monte_carlo",
    "track_milestones",
    "optimize_schedule",
    "what_if_analysis",
    "generate_schedule_variants",
    "manage_baseline",
    "track_variance",
    "sprint_planning",
    "update_schedule",
    "get_schedule",
]
