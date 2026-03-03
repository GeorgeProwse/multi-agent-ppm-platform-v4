"""
Action handlers for the Approval Workflow Agent.

Each module contains a focused set of action logic:
- create_approval: Approval chain creation, approver determination, delegation
- decision_actions: Recording approval/rejection decisions
- escalation_actions: Escalation scheduling and notification
- notification_actions: Notification subscription management
- notification_delivery: Notification sending, dispatch, and metrics
- lifecycle: Service Bus and Microsoft Graph initialization
"""

from actions.create_approval import (
    apply_delegations,
    assess_risk_and_criticality,
    create_approval_chain,
    determine_approvers,
    resolve_escalation_timeout,
)
from actions.decision_actions import record_decision
from actions.escalation_actions import schedule_escalations, send_escalation_notifications
from actions.notification_actions import handle_notification_action
from actions.notification_delivery import (
    send_approval_notifications,
    send_digest_notifications,
)

__all__ = [
    "apply_delegations",
    "assess_risk_and_criticality",
    "create_approval_chain",
    "determine_approvers",
    "handle_notification_action",
    "record_decision",
    "resolve_escalation_timeout",
    "schedule_escalations",
    "send_approval_notifications",
    "send_digest_notifications",
    "send_escalation_notifications",
]
