"""
Workflow & Process Engine Agent

Purpose:
Orchestrates complex workflows and processes across the PPM platform, providing dynamic
workflow execution, state management, and human task coordination.

Specification: agents/operations-management/workflow-engine-lib/README.md
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from observability.tracing import get_trace_id
from workflow_spec import WorkflowSpecError
from workflow_state_store import WorkflowStateStore, build_workflow_state_store
from workflow_task_queue import WorkflowTaskQueue, build_task_message, build_task_queue

from agents.runtime import BaseAgent, ServiceBusEventBus, get_event_bus
from agents.runtime.src.audit import build_audit_event, emit_audit_event

from workflow_actions import (
    handle_assign_task,
    handle_cancel_workflow,
    handle_complete_task,
    handle_define_workflow,
    handle_deploy_bpmn_workflow,
    handle_get_task_inbox,
    handle_get_workflow_instances,
    handle_get_workflow_status,
    handle_handle_event,
    handle_pause_workflow,
    handle_resume_workflow,
    handle_retry_failed_task,
    handle_start_workflow,
    handle_upload_bpmn_workflow,
    run_worker_once as _run_worker_once,
)


class WorkflowEngineAgent(BaseAgent):
    """
    Workflow & Process Engine Agent - Orchestrates workflows and processes.

    Key Capabilities:
    - Process definition and modeling
    - Workflow execution and orchestration
    - Event-driven triggers
    - Human task management
    - Dynamic workflow adaptation
    - Process versioning and rollback
    - Monitoring and analytics
    - Exception handling and compensation
    """

    def __init__(self, agent_id: str = "approval-workflow-agent", config: dict[str, Any] | None = None):
        super().__init__(agent_id, config)

        config = config or {}

        # Configuration parameters
        self.default_timeout_minutes = config.get("default_timeout_minutes", 60)
        self.max_retry_attempts = config.get("max_retry_attempts", 3)
        self.max_parallel_tasks = config.get("max_parallel_tasks", 10)
        self.worker_id = config.get("worker_id", os.getenv("WORKFLOW_WORKER_ID", self.agent_id))
        self.durable_config_path = Path(
            config.get(
                "durable_workflows_config",
                os.getenv("DURABLE_WORKFLOW_CONFIG", "ops/config/agents/approval-workflow-agent/durable_workflows.yaml"),
            )
        )
        self.monitoring_enabled = config.get("enable_monitoring", True)
        self.event_grid_enabled = config.get("enable_event_grid", True)
        self.logic_apps_endpoint = config.get("logic_apps_endpoint") or os.getenv(
            "LOGIC_APPS_ENDPOINT"
        )
        self.workflow_templates_path = Path(
            config.get(
                "workflow_templates_path",
                os.getenv("WORKFLOW_TEMPLATES_PATH", "ops/config/agents/approval-workflow-agent/workflow_templates.yaml"),
            )
        )
        self.rbac_policy = config.get(
            "rbac_policy",
            {
                "define_workflow": {"workflow_admin", "workflow_editor"},
                "start_workflow": {"workflow_admin", "workflow_operator"},
                "assign_task": {"workflow_admin", "workflow_operator"},
                "complete_task": {"workflow_admin", "workflow_operator"},
                "cancel_workflow": {"workflow_admin"},
                "pause_workflow": {"workflow_admin", "workflow_operator"},
                "resume_workflow": {"workflow_admin", "workflow_operator"},
                "retry_failed_task": {"workflow_admin", "workflow_operator"},
                "deploy_bpmn_workflow": {"workflow_admin", "workflow_editor"},
                "upload_bpmn_workflow": {"workflow_admin", "workflow_editor"},
            },
        )

        self.state_store: WorkflowStateStore = config.get("workflow_state_store") or (
            build_workflow_state_store(config)
        )
        self.task_queue: WorkflowTaskQueue = config.get("workflow_task_queue") or (
            build_task_queue(config)
        )

        # Cached state
        self.workflow_definitions = {}  # type: ignore
        self.workflow_instances = {}  # type: ignore
        self.task_assignments = {}  # type: ignore
        self.event_subscriptions = {}  # type: ignore
        self.durable_orchestrations = {}  # type: ignore
        self.event_bus = config.get("event_bus")
        if self.event_bus is None:
            service_bus_connection = config.get("service_bus_connection_string") or os.getenv(
                "SERVICE_BUS_CONNECTION_STRING"
            )
            if service_bus_connection:
                self.event_bus = ServiceBusEventBus(
                    connection_string=service_bus_connection,
                    topic_name=config.get("service_bus_topic", "ppm-events"),
                    subscription_name=config.get("service_bus_subscription"),
                )
            else:
                try:
                    self.event_bus = get_event_bus()
                except ValueError:
                    self.event_bus = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Initialize workflow orchestration services and integrations."""
        await super().initialize()
        self.logger.info("Initializing Workflow & Process Engine Agent...")
        await self.state_store.initialize()
        await self._load_durable_workflows_config()
        await self._load_workflow_templates()

        if isinstance(self.event_bus, ServiceBusEventBus):
            self.event_bus.subscribe("workflow.triggers", self._handle_service_bus_trigger)
            await self.event_bus.start()

        # Azure Durable Functions orchestration is represented by durable orchestrations
        # tracked in memory and persisted to the workflow state store.

        self.logger.info("Workflow & Process Engine Agent initialized")

    async def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate input data based on the requested action."""
        action = input_data.get("action", "")

        if not action:
            self.logger.warning("No action specified")
            return False

        valid_actions = [
            "define_workflow",
            "start_workflow",
            "get_workflow_status",
            "assign_task",
            "complete_task",
            "cancel_workflow",
            "pause_workflow",
            "resume_workflow",
            "handle_event",
            "retry_failed_task",
            "get_workflow_instances",
            "get_task_inbox",
            "deploy_bpmn_workflow",
            "upload_bpmn_workflow",
        ]

        if action not in valid_actions:
            self.logger.warning("Invalid action: %s", action)
            return False

        if action == "define_workflow":
            if "workflow" not in input_data:
                self.logger.warning("Missing workflow definition")
                return False

        elif action == "start_workflow":
            if "workflow_id" not in input_data:
                self.logger.warning("Missing workflow_id")
                return False
        elif action == "deploy_bpmn_workflow":
            if "bpmn_xml" not in input_data:
                self.logger.warning("Missing BPMN XML payload")
                return False
        elif action == "upload_bpmn_workflow":
            if "bpmn_xml" not in input_data and "bpmn_path" not in input_data:
                self.logger.warning("Missing BPMN XML payload or file path")
                return False

        return True

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process workflow and orchestration requests.

        Args:
            input_data: {
                "action": "define_workflow" | "start_workflow" | "get_workflow_status" |
                          "assign_task" | "complete_task" | "cancel_workflow" |
                          "pause_workflow" | "resume_workflow" | "handle_event" |
                          "retry_failed_task" | "get_workflow_instances" | "get_task_inbox",
                          "deploy_bpmn_workflow",
                "workflow": Workflow definition (BPMN or JSON),
                "workflow_id": Workflow definition ID,
                "instance_id": Workflow instance ID,
                "task_id": Task identifier,
                "event": Event data,
                "input_variables": Workflow input variables,
                "task_result": Task completion result,
                "assignee": Task assignee,
                "filters": Query filters,
                "bpmn_xml": BPMN 2.0 XML string
            }

        Returns:
            Response based on action:
            - define_workflow: Workflow ID and validation results
            - start_workflow: Instance ID and initial state
            - get_workflow_status: Instance status and current state
            - assign_task: Assignment confirmation
            - complete_task: Task completion and next steps
            - cancel_workflow: Cancellation confirmation
            - pause_workflow: Pause confirmation
            - resume_workflow: Resume confirmation
            - handle_event: Event handling result
            - retry_failed_task: Retry result
            - get_workflow_instances: List of instances
            - get_task_inbox: User's pending tasks
            - deploy_bpmn_workflow: Deployment status for BPMN workflows
        """
        action = input_data.get("action", "get_workflow_instances")
        tenant_id = (
            input_data.get("tenant_id")
            or input_data.get("context", {}).get("tenant_id")
            or "default"
        )
        self._authorize_action(action, input_data)

        if action == "define_workflow":
            return await handle_define_workflow(self, tenant_id, input_data.get("workflow", {}))

        elif action == "start_workflow":
            return await handle_start_workflow(
                self,
                tenant_id,
                input_data.get("workflow_id"),
                input_data.get("input_variables", {}),  # type: ignore
            )

        elif action == "get_workflow_status":
            return await handle_get_workflow_status(
                self, tenant_id, input_data.get("instance_id")  # type: ignore
            )

        elif action == "assign_task":
            return await handle_assign_task(
                self, tenant_id, input_data.get("task_id"), input_data.get("assignee")  # type: ignore
            )

        elif action == "complete_task":
            return await handle_complete_task(
                self, tenant_id, input_data.get("task_id"), input_data.get("task_result", {})  # type: ignore
            )

        elif action == "cancel_workflow":
            return await handle_cancel_workflow(self, tenant_id, input_data.get("instance_id"))  # type: ignore

        elif action == "pause_workflow":
            return await handle_pause_workflow(self, tenant_id, input_data.get("instance_id"))  # type: ignore

        elif action == "resume_workflow":
            return await handle_resume_workflow(self, tenant_id, input_data.get("instance_id"))  # type: ignore

        elif action == "handle_event":
            return await handle_handle_event(self, tenant_id, input_data.get("event", {}))

        elif action == "retry_failed_task":
            return await handle_retry_failed_task(self, tenant_id, input_data.get("task_id"))  # type: ignore

        elif action == "get_workflow_instances":
            return await handle_get_workflow_instances(self, tenant_id, input_data.get("filters", {}))

        elif action == "get_task_inbox":
            return await handle_get_task_inbox(self, tenant_id, input_data.get("user_id"))  # type: ignore

        elif action == "deploy_bpmn_workflow":
            return await handle_deploy_bpmn_workflow(
                self,
                tenant_id,
                input_data.get("bpmn_xml"),  # type: ignore
                input_data.get("workflow_name"),
            )
        elif action == "upload_bpmn_workflow":
            return await handle_upload_bpmn_workflow(
                self,
                tenant_id,
                input_data.get("bpmn_xml"),
                input_data.get("bpmn_path"),
                input_data.get("workflow_name"),
            )

        else:
            raise ValueError(f"Unknown action: {action}")

    # ------------------------------------------------------------------
    # Shared infrastructure (used by action handlers via ``agent`` ref)
    # ------------------------------------------------------------------

    async def _execute_task(self, tenant_id: str, instance_id: str, task: dict[str, Any]) -> None:
        """Execute workflow task."""
        task_id = task.get("task_id")

        # Create task assignment
        assignment = {
            "task_id": task_id,
            "instance_id": instance_id,
            "task_type": task.get("type"),
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "task_payload": task,
            "retry_policy": task.get("retry_policy"),
            "compensation_task_id": task.get("compensation_task_id"),
        }
        self.task_assignments[task_id] = assignment
        await self.state_store.save_task(tenant_id, task_id, assignment.copy())

        # Add to instance current tasks
        instance = await self._load_instance(tenant_id, instance_id)
        if instance:
            instance.get("current_tasks", []).append(task_id)
            await self.state_store.save_instance(tenant_id, instance_id, instance.copy())

        await self.task_queue.publish_task(
            build_task_message(
                tenant_id=tenant_id,
                instance_id=instance_id,
                task_id=task_id,
                task_type=task.get("type"),
                payload={"workflow_id": instance.get("workflow_id") if instance else None},
            )
        )

    async def _trigger_compensation(
        self, tenant_id: str, instance: dict[str, Any], reason: str
    ) -> None:
        workflow_id = instance.get("workflow_id")
        workflow = await self._load_definition(tenant_id, workflow_id) if workflow_id else None
        if not workflow:
            return
        compensation_tasks = []
        completed_steps = list(instance.get("completed_steps", []))
        failed_steps = list(instance.get("failed_tasks", []))
        for task_id in completed_steps + failed_steps:
            task = next(
                (item for item in workflow.get("tasks", []) if item.get("task_id") == task_id),
                None,
            )
            if task and task.get("compensation_task_id"):
                comp_task = next(
                    (
                        item
                        for item in workflow.get("tasks", [])
                        if item.get("task_id") == task.get("compensation_task_id")
                    ),
                    None,
                )
                if comp_task:
                    compensation_tasks.append(comp_task)

        if not compensation_tasks:
            return

        instance["status"] = "compensating"
        await self.state_store.save_instance(tenant_id, instance["instance_id"], instance.copy())
        await self._emit_workflow_event(
            tenant_id,
            "workflow.compensation.started",
            {"instance_id": instance["instance_id"], "reason": reason},
        )
        await self._send_notification(
            tenant_id,
            "workflow.compensation.started",
            {"instance_id": instance["instance_id"], "reason": reason},
        )

        for task in compensation_tasks:
            await self._execute_task(tenant_id, instance["instance_id"], task)

        instance.setdefault("compensation_history", []).append(
            {
                "reason": reason,
                "tasks": [task.get("task_id") for task in compensation_tasks],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        await self.state_store.save_instance(tenant_id, instance["instance_id"], instance.copy())
        await self._emit_workflow_event(
            tenant_id,
            "workflow.compensation.completed",
            {
                "instance_id": instance["instance_id"],
                "tasks": [t.get("task_id") for t in compensation_tasks],
            },
        )
        await self._send_notification(
            tenant_id,
            "workflow.compensation.completed",
            {
                "instance_id": instance["instance_id"],
                "tasks": [t.get("task_id") for t in compensation_tasks],
            },
        )

    async def _register_event_triggers(
        self, tenant_id: str, workflow_id: str, triggers: list[dict[str, Any]]
    ) -> None:
        """Register event triggers for a workflow definition."""
        for trigger in triggers:
            subscription_id = f"SUB-{len(self.event_subscriptions) + 1}"
            subscription = {
                "subscription_id": subscription_id,
                "workflow_id": workflow_id,
                "event_type": trigger.get("event_type"),
                "criteria": trigger.get("criteria", {}),
                "action": trigger.get("action", "start"),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "task_id": trigger.get("task_id"),
            }
            self.event_subscriptions[subscription_id] = subscription
            await self.state_store.save_subscription(
                tenant_id, subscription_id, subscription.copy()
            )

    async def _find_event_subscriptions(
        self, tenant_id: str, event_type: str
    ) -> list[dict[str, Any]]:
        """Find workflows subscribed to event type."""
        subscriptions = await self.state_store.list_subscriptions(tenant_id, event_type=event_type)
        for subscription in subscriptions:
            if subscription.get("subscription_id"):
                self.event_subscriptions[subscription["subscription_id"]] = subscription
        return subscriptions

    async def _event_matches_criteria(
        self, event_data: dict[str, Any], criteria: dict[str, Any]
    ) -> bool:
        """Delegate to engine_utils.event_matches_criteria (kept for backward compat)."""
        from engine_utils import event_matches_criteria

        return await event_matches_criteria(event_data, criteria)

    # ------------------------------------------------------------------
    # Eventing / notifications / telemetry
    # ------------------------------------------------------------------

    async def _emit_workflow_event(
        self, tenant_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        """Emit workflow events for audit/analytics."""
        event_id = f"WF-EVT-{len(self.workflow_instances) + 1}"
        event_record = {
            "event_id": event_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self.state_store.save_event(tenant_id, event_id, event_record)
        audit_event = build_audit_event(
            tenant_id=tenant_id,
            action=event_type,
            outcome="success",
            actor_id=self.agent_id,
            actor_type="service",
            actor_roles=[],
            resource_id=payload.get("instance_id") or payload.get("workflow_id") or event_id,
            resource_type="workflow_event",
            metadata={"event_id": event_id},
            trace_id=get_trace_id(),
        )
        emit_audit_event(audit_event)
        if self.event_bus:
            await self.event_bus.publish("workflow.events", event_record)
            await self.event_bus.publish("workflow.notifications", event_record)
        await self._emit_monitor_telemetry(tenant_id, event_type, payload)
        await self._emit_event_grid_event(tenant_id, event_type, payload)

    async def _emit_monitor_telemetry(
        self, tenant_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        if not self.monitoring_enabled:
            return
        telemetry_payload = {
            "tenant_id": tenant_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "workflow_engine_agent",
        }
        if self.event_bus:
            await self.event_bus.publish("azure.monitor.telemetry", telemetry_payload)

    async def _emit_event_grid_event(
        self, tenant_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        if not self.event_grid_enabled:
            return
        event_grid_payload = {
            "tenant_id": tenant_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "workflow_engine_agent",
        }
        if self.event_bus:
            await self.event_bus.publish("azure.eventgrid.events", event_grid_payload)

    async def _invoke_logic_app(self, tenant_id: str, assignment: dict[str, Any]) -> None:
        payload = {
            "tenant_id": tenant_id,
            "task_id": assignment.get("task_id"),
            "instance_id": assignment.get("instance_id"),
            "payload": assignment.get("task_payload", {}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if self.logic_apps_endpoint:
            self.logger.info(
                "Logic Apps invocation scheduled",
                extra={"endpoint": self.logic_apps_endpoint, "task_id": assignment.get("task_id")},
            )
        if self.event_bus:
            await self.event_bus.publish("logic.apps.invocations", payload)

    async def _send_notification(
        self, tenant_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        notification = {
            "tenant_id": tenant_id,
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "workflow_engine_agent",
        }
        if self.event_bus:
            await self.event_bus.publish("workflow.notifications", notification)

    # ------------------------------------------------------------------
    # Data access helpers
    # ------------------------------------------------------------------

    async def _load_definition(self, tenant_id: str, workflow_id: str) -> dict[str, Any] | None:
        cache_key = f"{tenant_id}:{workflow_id}"
        workflow = self.workflow_definitions.get(cache_key)
        if workflow:
            return workflow
        stored = await self.state_store.get_definition(tenant_id, workflow_id)
        if stored:
            self.workflow_definitions[cache_key] = stored
        return stored

    async def _load_instance(self, tenant_id: str, instance_id: str) -> dict[str, Any] | None:
        instance = self.workflow_instances.get(instance_id)
        if instance:
            return instance
        stored = await self.state_store.get_instance(tenant_id, instance_id)
        if stored:
            self.workflow_instances[instance_id] = stored
        return stored

    async def _load_task_assignment(self, tenant_id: str, task_id: str) -> dict[str, Any] | None:
        assignment = self.task_assignments.get(task_id)
        if assignment:
            return assignment
        stored = await self.state_store.get_task(tenant_id, task_id)
        if stored:
            self.task_assignments[task_id] = stored
        return stored

    # ------------------------------------------------------------------
    # Config loaders
    # ------------------------------------------------------------------

    async def _load_durable_workflows_config(self) -> None:
        if not self.durable_config_path.exists():
            self.logger.info(
                "Durable workflow config not found", extra={"path": str(self.durable_config_path)}
            )
            return
        config_payload = yaml.safe_load(self.durable_config_path.read_text()) or {}
        workflows = config_payload.get("workflows", [])
        for workflow in workflows:
            steps = workflow.get("steps", [])
            tasks = []
            transitions = []
            for index, step in enumerate(steps):
                if index + 1 < len(steps):
                    transitions.append(
                        {"source": step.get("task_id"), "target": steps[index + 1].get("task_id")}
                    )
                tasks.append(
                    {
                        "task_id": step.get("task_id"),
                        "name": step.get("name"),
                        "type": step.get("type", "automated"),
                        "initial": index == 0,
                        "retry_policy": step.get("retry_policy"),
                        "compensation_task_id": step.get("compensation_task_id"),
                    }
                )
            workflow_config = {
                "name": workflow.get("name") or workflow.get("workflow_id"),
                "description": workflow.get("description"),
                "tasks": tasks,
                "transitions": transitions,
                "definition_source": "durable_config",
                "version": workflow.get("version", 1),
            }
            await handle_define_workflow(self, "default", workflow_config)

    async def _handle_service_bus_trigger(self, payload: dict[str, Any]) -> None:
        tenant_id = payload.get("tenant_id") or "default"
        await handle_handle_event(self, tenant_id, payload)

    async def _load_workflow_templates(self) -> None:
        if not self.workflow_templates_path.exists():
            self.logger.info(
                "Workflow templates not found", extra={"path": str(self.workflow_templates_path)}
            )
            return
        templates = yaml.safe_load(self.workflow_templates_path.read_text()) or {}
        for template in templates.get("templates", []):
            try:
                await handle_define_workflow(self, "default", template)
            except WorkflowSpecError as exc:
                self.logger.warning(
                    "Template invalid", extra={"template": template.get("name"), "error": str(exc)}
                )

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    async def run_worker_once(self) -> dict[str, Any] | None:
        return await _run_worker_once(self)

    # ------------------------------------------------------------------
    # Cleanup / capabilities
    # ------------------------------------------------------------------

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info("Cleaning up Workflow & Process Engine Agent...")
        if isinstance(self.event_bus, ServiceBusEventBus):
            await self.event_bus.stop()

    def get_capabilities(self) -> list[str]:
        """Return list of agent capabilities."""
        return [
            "workflow_definition",
            "workflow_orchestration",
            "process_execution",
            "human_task_management",
            "event_driven_triggers",
            "dynamic_adaptation",
            "process_versioning",
            "exception_handling",
            "compensation",
            "workflow_monitoring",
            "bpmn_support",
            "state_management",
        ]

    def _authorize_action(self, action: str, input_data: dict[str, Any]) -> None:
        required_roles = self.rbac_policy.get(action)
        if not required_roles:
            return
        actor = input_data.get("actor") or {}
        roles = actor.get("roles") or input_data.get("context", {}).get("roles") or []
        # When no actor/roles are present the call originates from an internal
        # system context (e.g. another agent or a unit test).  Allow it through
        # so that callers that don't carry user credentials are not blocked.
        if not roles:
            return
        if not set(roles).intersection(required_roles):
            raise PermissionError(f"Actor lacks required role for {action}")
