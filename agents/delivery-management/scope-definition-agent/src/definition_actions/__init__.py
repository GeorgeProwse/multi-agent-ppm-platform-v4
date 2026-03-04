"""
Action handlers for the Project Definition & Scope Agent.

Each module contains the implementation for one (or a small group of related) actions,
extracted from the monolithic ProjectDefinitionAgent class to improve readability and
maintainability.  All handlers follow the same signature convention:

    async def handle_<action>(agent: "ProjectDefinitionAgent", ...) -> dict[str, Any]

The agent instance is passed explicitly so that handlers can access stores, services,
and configuration without requiring inheritance.
"""

from definition_actions.baseline_actions import (
    handle_detect_scope_creep,
    handle_manage_scope_baseline,
)
from definition_actions.charter_actions import handle_generate_charter, handle_get_charter
from definition_actions.requirements_actions import (
    handle_create_traceability_matrix,
    handle_get_requirements,
    handle_manage_requirements,
)
from definition_actions.scope_research_actions import handle_generate_scope_research
from definition_actions.stakeholder_actions import (
    handle_analyze_stakeholders,
    handle_create_raci_matrix,
)
from definition_actions.wbs_actions import handle_generate_wbs, handle_get_wbs, handle_update_wbs

__all__ = [
    "handle_detect_scope_creep",
    "handle_generate_charter",
    "handle_generate_scope_research",
    "handle_generate_wbs",
    "handle_get_charter",
    "handle_get_requirements",
    "handle_get_wbs",
    "handle_manage_requirements",
    "handle_manage_scope_baseline",
    "handle_create_traceability_matrix",
    "handle_analyze_stakeholders",
    "handle_create_raci_matrix",
    "handle_update_wbs",
]
