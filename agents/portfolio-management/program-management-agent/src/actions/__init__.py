"""
Action handlers for the Program Management Agent.

Each module in this package implements one or more action handlers that are
delegated to from the main ``ProgramManagementAgent.process()`` router.
"""

from actions.create_program import handle_create_program, handle_get_program
from actions.generate_roadmap import handle_generate_roadmap
from actions.track_dependencies import handle_track_dependencies
from actions.aggregate_benefits import handle_aggregate_benefits
from actions.coordinate_resources import handle_coordinate_resources
from actions.identify_synergies import handle_identify_synergies
from actions.analyze_change_impact import handle_analyze_change_impact
from actions.get_program_health import handle_get_program_health
from actions.optimize_program import handle_optimize_program
from actions.approval_actions import handle_submit_program_for_approval, handle_record_program_decision

__all__ = [
    "handle_create_program",
    "handle_get_program",
    "handle_generate_roadmap",
    "handle_track_dependencies",
    "handle_aggregate_benefits",
    "handle_coordinate_resources",
    "handle_identify_synergies",
    "handle_analyze_change_impact",
    "handle_get_program_health",
    "handle_optimize_program",
    "handle_submit_program_for_approval",
    "handle_record_program_decision",
]
