"""
Action handlers for the Program Management Agent.

Each module in this package implements one or more action handlers that are
delegated to from the main ``ProgramManagementAgent.process()`` router.
"""

from program_actions.create_program import handle_create_program, handle_get_program
from program_actions.generate_roadmap import handle_generate_roadmap
from program_actions.track_dependencies import handle_track_dependencies
from program_actions.aggregate_benefits import handle_aggregate_benefits
from program_actions.coordinate_resources import handle_coordinate_resources
from program_actions.identify_synergies import handle_identify_synergies
from program_actions.analyze_change_impact import handle_analyze_change_impact
from program_actions.get_program_health import handle_get_program_health
from program_actions.optimize_program import handle_optimize_program
from program_actions.approval_actions import handle_submit_program_for_approval, handle_record_program_decision

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
