"""
Compliance & Regulatory Agent - Action Handlers

Each action is implemented in its own module and exposes a ``handle_*`` entry point
that receives the agent instance and action-specific arguments.
"""

from actions.add_regulation import handle_add_regulation
from actions.assess_compliance import handle_assess_compliance
from actions.audit import handle_conduct_audit, handle_prepare_audit
from actions.dashboard import handle_get_compliance_dashboard
from actions.define_control import handle_define_control
from actions.evidence import handle_get_evidence, handle_list_evidence, handle_upload_evidence
from actions.manage_policy import handle_manage_policy
from actions.map_controls import handle_map_controls_to_project
from actions.monitor_regulatory import (
    handle_monitor_regulations,
    handle_monitor_regulatory_changes,
)
from actions.release_compliance import handle_verify_release_compliance
from actions.reporting import handle_generate_compliance_report, handle_get_report, handle_list_reports

__all__ = [
    "handle_add_regulation",
    "handle_assess_compliance",
    "handle_conduct_audit",
    "handle_define_control",
    "handle_generate_compliance_report",
    "handle_get_compliance_dashboard",
    "handle_get_evidence",
    "handle_get_report",
    "handle_list_evidence",
    "handle_list_reports",
    "handle_manage_policy",
    "handle_map_controls_to_project",
    "handle_monitor_regulations",
    "handle_monitor_regulatory_changes",
    "handle_prepare_audit",
    "handle_upload_evidence",
    "handle_verify_release_compliance",
]
