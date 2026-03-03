"""Release & Deployment Agent - Action handlers package.

Each sub-module contains a single top-level async function that implements
one (or a small group of closely related) agent actions.  The main
``ReleaseDeploymentAgent`` class delegates to these functions from its
``process()`` router.
"""

from actions.assess_readiness import assess_readiness
from actions.create_deployment_plan import create_deployment_plan
from actions.deployment_metrics import track_deployment_metrics
from actions.execute_deployment import execute_deployment
from actions.manage_environment import check_configuration_drift, manage_environment
from actions.plan_release import plan_release
from actions.query_status import (
    get_deployment_history,
    get_deployment_status,
    get_release_calendar,
    get_release_status,
)
from actions.release_notes import generate_release_notes
from actions.rollback_deployment import rollback_deployment
from actions.schedule_window import schedule_deployment_window
from actions.verify_post_deployment import verify_post_deployment

__all__ = [
    "assess_readiness",
    "check_configuration_drift",
    "create_deployment_plan",
    "execute_deployment",
    "generate_release_notes",
    "get_deployment_history",
    "get_deployment_status",
    "get_release_calendar",
    "get_release_status",
    "manage_environment",
    "plan_release",
    "rollback_deployment",
    "schedule_deployment_window",
    "track_deployment_metrics",
    "verify_post_deployment",
]
