# Repository Index

Complete file and folder structure of the repository.

```
multi-agent-ppm-platform-v4/
├── .claude
│   ├── hooks
│   │   └── session-start.sh
│   └── settings.json
├── .devcontainer
│   ├── Dockerfile
│   ├── dev.env
│   └── devcontainer.json
├── .dockerignore
├── .gitattributes
├── .github
│   ├── CODEOWNERS
│   ├── README.md
│   ├── dependabot.yml
│   ├── issue_template
│   │   ├── bug_report.md
│   │   ├── config.yml
│   │   ├── documentation.md
│   │   ├── feature_request.md
│   │   └── security_issue.md
│   ├── pull_request_template.md
│   ├── renovate.json
│   └── workflows
│       ├── README.md
│       ├── cd.yml
│       ├── ci.yml
│       ├── connectors-live-smoke.yml
│       ├── container-scan.yml
│       ├── contract-tests.yml
│       ├── dast-staging.yml
│       ├── dependency-audit.yml
│       ├── e2e-tests.yml
│       ├── iac-scan.yml
│       ├── license-compliance.yml
│       ├── migration-check.yml
│       ├── performance-smoke.yml
│       ├── pr-labeler.yml
│       ├── pr.yml
│       ├── promotion.yml
│       ├── release-gate.yml
│       ├── release.yml
│       ├── sbom.yml
│       ├── secret-scan.yml
│       ├── security-scan.yml
│       ├── static.yml
│       └── storybook-visual-regression.yml
├── .gitignore
├── .gitleaks.toml
├── .pre-commit-config.yaml
├── CLAUDE.md
├── CONTRIBUTING.md
├── INDEX.md
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── agents
│   ├── AGENT_CATALOG.md
│   ├── README.md
│   ├── __init__.py
│   ├── common
│   │   ├── __init__.py
│   │   ├── connector_integration.py
│   │   ├── health_recommendations.py
│   │   ├── integration_services.py
│   │   ├── metrics_catalog.py
│   │   ├── scenario.py
│   │   └── web_search.py
│   ├── core-orchestration
│   │   ├── README.md
│   │   ├── approval-workflow-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── create_approval.py
│   │   │   │   │   ├── decision_actions.py
│   │   │   │   │   ├── escalation_actions.py
│   │   │   │   │   ├── lifecycle.py
│   │   │   │   │   ├── notification_actions.py
│   │   │   │   │   └── notification_delivery.py
│   │   │   │   ├── approval_utils.py
│   │   │   │   ├── approval_workflow_agent.py
│   │   │   │   ├── engine_infra.py
│   │   │   │   ├── engine_utils.py
│   │   │   │   ├── templates
│   │   │   │   │   ├── en
│   │   │   │   │   │   └── approval_notification.md
│   │   │   │   │   └── fr
│   │   │   │   │       └── approval_notification.md
│   │   │   │   ├── workflow_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── assign_task.py
│   │   │   │   │   ├── cancel_workflow.py
│   │   │   │   │   ├── complete_task.py
│   │   │   │   │   ├── define_workflow.py
│   │   │   │   │   ├── deploy_bpmn.py
│   │   │   │   │   ├── get_workflow_status.py
│   │   │   │   │   ├── handle_event.py
│   │   │   │   │   ├── pause_resume_workflow.py
│   │   │   │   │   ├── query_workflows.py
│   │   │   │   │   ├── retry_failed_task.py
│   │   │   │   │   ├── start_workflow.py
│   │   │   │   │   └── worker.py
│   │   │   │   ├── workflow_engine_agent.py
│   │   │   │   ├── workflow_spec.py
│   │   │   │   ├── workflow_state_store.py
│   │   │   │   └── workflow_task_queue.py
│   │   │   └── workflows
│   │   │       └── schema
│   │   │           └── workflow_spec.schema.json
│   │   ├── intent-router-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── models
│   │   │   │   └── intent_classifier
│   │   │   │       └── README.md
│   │   │   ├── src
│   │   │   │   ├── intent_router_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── routing_actions.py
│   │   │   │   ├── intent_router_agent.py
│   │   │   │   ├── intent_router_models.py
│   │   │   │   └── intent_router_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_intent_router_agent.py
│   │   ├── response-orchestration-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── plan_schema.py
│   │   │   │   ├── response_orchestration_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── orchestration_actions.py
│   │   │   │   ├── response_orchestration_agent.py
│   │   │   │   ├── response_orchestration_models.py
│   │   │   │   └── response_orchestration_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_response_orchestration_agent.py
│   │   └── workspace-setup-agent
│   │       ├── Dockerfile
│   │       ├── README.md
│   │       ├── demo-fixtures
│   │       │   └── sample-response.json
│   │       ├── src
│   │       │   └── workspace_setup_agent.py
│   │       └── tests
│   │           ├── README.md
│   │           └── test_workspace_setup_agent.py
│   ├── delivery-management
│   │   ├── README.md
│   │   ├── compliance-governance-agent
│   │   │   ├── COMPLIANCE_CONTROL_CATALOG.md
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── compliance_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── add_regulation.py
│   │   │   │   │   ├── assess_compliance.py
│   │   │   │   │   ├── audit.py
│   │   │   │   │   ├── dashboard.py
│   │   │   │   │   ├── define_control.py
│   │   │   │   │   ├── evidence.py
│   │   │   │   │   ├── manage_policy.py
│   │   │   │   │   ├── map_controls.py
│   │   │   │   │   ├── monitor_regulatory.py
│   │   │   │   │   ├── release_compliance.py
│   │   │   │   │   ├── reporting.py
│   │   │   │   │   └── test_control.py
│   │   │   │   ├── compliance_models.py
│   │   │   │   ├── compliance_regulatory_agent.py
│   │   │   │   ├── compliance_seed.py
│   │   │   │   └── compliance_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_compliance_regulatory_agent.py
│   │   ├── financial-management-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── financial_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── budget_actions.py
│   │   │   │   │   ├── cost_actions.py
│   │   │   │   │   ├── evm_actions.py
│   │   │   │   │   ├── forecast_actions.py
│   │   │   │   │   ├── profitability_actions.py
│   │   │   │   │   ├── report_actions.py
│   │   │   │   │   └── variance_actions.py
│   │   │   │   ├── financial_management_agent.py
│   │   │   │   ├── financial_models.py
│   │   │   │   └── financial_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_financial_management_agent.py
│   │   ├── lifecycle-governance-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── lifecycle_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── evaluate_gate.py
│   │   │   │   │   ├── initiate_project.py
│   │   │   │   │   ├── monitor_health.py
│   │   │   │   │   ├── override_gate.py
│   │   │   │   │   ├── query_actions.py
│   │   │   │   │   ├── readiness_actions.py
│   │   │   │   │   ├── recommend_methodology.py
│   │   │   │   │   └── transition_phase.py
│   │   │   │   ├── lifecycle_persistence.py
│   │   │   │   ├── lifecycle_utils.py
│   │   │   │   ├── monitoring.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── orchestration.py
│   │   │   │   ├── project_lifecycle_agent.py
│   │   │   │   ├── readiness_model.py
│   │   │   │   ├── summarization.py
│   │   │   │   └── sync_clients.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_lifecycle_agent.py
│   │   ├── quality-management-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── quality_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── analysis_actions.py
│   │   │   │   │   ├── audit_actions.py
│   │   │   │   │   ├── defect_actions.py
│   │   │   │   │   ├── metric_actions.py
│   │   │   │   │   ├── plan_actions.py
│   │   │   │   │   ├── reporting_actions.py
│   │   │   │   │   ├── requirement_actions.py
│   │   │   │   │   ├── review_actions.py
│   │   │   │   │   └── test_actions.py
│   │   │   │   ├── quality_management_agent.py
│   │   │   │   ├── quality_models.py
│   │   │   │   └── quality_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_quality_management_agent.py
│   │   ├── resource-management-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── resource_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── allocation.py
│   │   │   │   │   ├── analytics.py
│   │   │   │   │   ├── demand_management.py
│   │   │   │   │   ├── helpers.py
│   │   │   │   │   ├── planning.py
│   │   │   │   │   ├── reporting.py
│   │   │   │   │   └── sync.py
│   │   │   │   ├── resource_capacity_agent.py
│   │   │   │   ├── resource_models.py
│   │   │   │   └── resource_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_resource_management_agent.py
│   │   ├── risk-management-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── data
│   │   │   │   └── feedback.sqlite3
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── risk_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── assess_risk.py
│   │   │   │   │   ├── create_mitigation_plan.py
│   │   │   │   │   ├── generate_risk_matrix.py
│   │   │   │   │   ├── generate_risk_report.py
│   │   │   │   │   ├── get_risk_dashboard.py
│   │   │   │   │   ├── get_top_risks.py
│   │   │   │   │   ├── identify_risk.py
│   │   │   │   │   ├── monitor_triggers.py
│   │   │   │   │   ├── prioritize_risks.py
│   │   │   │   │   ├── research_risks.py
│   │   │   │   │   ├── run_monte_carlo.py
│   │   │   │   │   ├── sensitivity_analysis.py
│   │   │   │   │   └── update_risk_status.py
│   │   │   │   ├── risk_management_agent.py
│   │   │   │   ├── risk_management_api.py
│   │   │   │   ├── risk_models.py
│   │   │   │   ├── risk_nlp_training.py
│   │   │   │   └── risk_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_risk_management_agent_delivery.py
│   │   ├── schedule-planning-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── schedule_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── baseline.py
│   │   │   │   │   ├── create_schedule.py
│   │   │   │   │   ├── critical_path.py
│   │   │   │   │   ├── estimate_duration.py
│   │   │   │   │   ├── map_dependencies.py
│   │   │   │   │   ├── milestones.py
│   │   │   │   │   ├── monte_carlo.py
│   │   │   │   │   ├── optimize.py
│   │   │   │   │   ├── resource_scheduling.py
│   │   │   │   │   ├── schedule_crud.py
│   │   │   │   │   ├── sprint_planning.py
│   │   │   │   │   └── what_if.py
│   │   │   │   ├── schedule_models.py
│   │   │   │   ├── schedule_planning_agent.py
│   │   │   │   └── schedule_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_schedule_planning_agent.py
│   │   ├── scope-definition-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── definition_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── baseline_actions.py
│   │   │   │   │   ├── charter_actions.py
│   │   │   │   │   ├── requirements_actions.py
│   │   │   │   │   ├── scope_research_actions.py
│   │   │   │   │   ├── stakeholder_actions.py
│   │   │   │   │   └── wbs_actions.py
│   │   │   │   ├── definition_models.py
│   │   │   │   ├── definition_utils.py
│   │   │   │   ├── project_definition_agent.py
│   │   │   │   ├── scope_research.py
│   │   │   │   └── web_search.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_scope_definition_agent.py
│   │   └── vendor-procurement-agent
│   │       ├── Dockerfile
│   │       ├── PROCUREMENT_WORKFLOW_BOUNDARIES.md
│   │       ├── README.md
│   │       ├── demo-fixtures
│   │       │   └── sample-response.json
│   │       ├── src
│   │       │   ├── vendor_actions
│   │       │   │   ├── __init__.py
│   │       │   │   ├── contract.py
│   │       │   │   ├── event_handlers.py
│   │       │   │   ├── invoice.py
│   │       │   │   ├── onboard_vendor.py
│   │       │   │   ├── procurement_request.py
│   │       │   │   ├── purchase_order.py
│   │       │   │   ├── research_vendor.py
│   │       │   │   ├── rfp.py
│   │       │   │   ├── vendor_performance.py
│   │       │   │   ├── vendor_profile.py
│   │       │   │   └── vendor_search.py
│   │       │   ├── vendor_models.py
│   │       │   ├── vendor_procurement_agent.py
│   │       │   └── vendor_utils.py
│   │       └── tests
│   │           ├── README.md
│   │           └── test_vendor_procurement_agent.py
│   ├── operations-management
│   │   ├── README.md
│   │   ├── analytics-insights-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── analytics_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── aggregate_data.py
│   │   │   │   │   ├── compute_kpis.py
│   │   │   │   │   ├── create_dashboard.py
│   │   │   │   │   ├── data_lineage.py
│   │   │   │   │   ├── generate_narrative.py
│   │   │   │   │   ├── generate_report.py
│   │   │   │   │   ├── infrastructure.py
│   │   │   │   │   ├── insights.py
│   │   │   │   │   ├── periodic_report.py
│   │   │   │   │   ├── query_data.py
│   │   │   │   │   ├── run_prediction.py
│   │   │   │   │   ├── scenario_analysis.py
│   │   │   │   │   └── track_kpi.py
│   │   │   │   ├── analytics_insights_agent.py
│   │   │   │   ├── analytics_models.py
│   │   │   │   └── analytics_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_analytics_insights_agent.py
│   │   ├── change-control-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── change_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── approve_and_review.py
│   │   │   │   │   ├── classify_and_assess.py
│   │   │   │   │   ├── cmdb_actions.py
│   │   │   │   │   ├── implement_change.py
│   │   │   │   │   ├── reporting.py
│   │   │   │   │   ├── submit_change.py
│   │   │   │   │   └── webhook_and_monitoring.py
│   │   │   │   ├── change_configuration_agent.py
│   │   │   │   ├── change_models.py
│   │   │   │   └── change_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_change_configuration_agent.py
│   │   ├── continuous-improvement-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── ci_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── benchmarking.py
│   │   │   │   │   ├── conformance.py
│   │   │   │   │   ├── discovery.py
│   │   │   │   │   ├── improvement.py
│   │   │   │   │   ├── ingest.py
│   │   │   │   │   ├── insights.py
│   │   │   │   │   └── root_cause.py
│   │   │   │   ├── mining_models.py
│   │   │   │   ├── mining_utils.py
│   │   │   │   └── process_mining_agent.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_process_mining_agent.py
│   │   ├── data-synchronisation-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── data_sync_agent.py
│   │   │   │   ├── sync_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── conflicts.py
│   │   │   │   │   ├── connectors.py
│   │   │   │   │   ├── duplicates.py
│   │   │   │   │   ├── master_records.py
│   │   │   │   │   ├── monitoring.py
│   │   │   │   │   ├── retry.py
│   │   │   │   │   ├── schema.py
│   │   │   │   │   ├── sync_data.py
│   │   │   │   │   └── validation.py
│   │   │   │   ├── sync_infrastructure.py
│   │   │   │   ├── sync_models.py
│   │   │   │   └── sync_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_data_sync_agent.py
│   │   ├── knowledge-management-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── knowledge_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── classification_actions.py
│   │   │   │   │   ├── collaboration_actions.py
│   │   │   │   │   ├── document_actions.py
│   │   │   │   │   ├── ingestion_actions.py
│   │   │   │   │   ├── knowledge_graph_actions.py
│   │   │   │   │   └── search_actions.py
│   │   │   │   ├── knowledge_db.py
│   │   │   │   ├── knowledge_management_agent.py
│   │   │   │   ├── knowledge_models.py
│   │   │   │   └── knowledge_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_knowledge_management_agent.py
│   │   ├── release-deployment-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── release_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── assess_readiness.py
│   │   │   │   │   ├── create_deployment_plan.py
│   │   │   │   │   ├── deployment_metrics.py
│   │   │   │   │   ├── execute_deployment.py
│   │   │   │   │   ├── manage_environment.py
│   │   │   │   │   ├── plan_release.py
│   │   │   │   │   ├── query_status.py
│   │   │   │   │   ├── release_notes.py
│   │   │   │   │   ├── rollback_deployment.py
│   │   │   │   │   ├── schedule_window.py
│   │   │   │   │   └── verify_post_deployment.py
│   │   │   │   ├── release_deployment_agent.py
│   │   │   │   ├── release_models.py
│   │   │   │   └── release_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_release_deployment_agent.py
│   │   ├── stakeholder-communications-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── __init__.py
│   │   │   │   ├── actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── briefing_actions.py
│   │   │   │   │   ├── classify_stakeholder.py
│   │   │   │   │   ├── communication_plan.py
│   │   │   │   │   ├── dashboard_actions.py
│   │   │   │   │   ├── delivery_actions.py
│   │   │   │   │   ├── engagement_actions.py
│   │   │   │   │   ├── event_actions.py
│   │   │   │   │   ├── feedback_actions.py
│   │   │   │   │   ├── message_actions.py
│   │   │   │   │   ├── preferences_actions.py
│   │   │   │   │   └── register_stakeholder.py
│   │   │   │   ├── stakeholder_communications_agent.py
│   │   │   │   ├── stakeholder_models.py
│   │   │   │   └── stakeholder_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_stakeholder_communications_agent.py
│   │   └── system-health-agent
│   │       ├── Dockerfile
│   │       ├── README.md
│   │       ├── demo-fixtures
│   │       │   └── sample-response.json
│   │       ├── src
│   │       │   ├── health_actions
│   │       │   │   ├── __init__.py
│   │       │   │   ├── alert_management.py
│   │       │   │   ├── anomaly_detection.py
│   │       │   │   ├── capacity_planning.py
│   │       │   │   ├── check_health.py
│   │       │   │   ├── collect_metrics.py
│   │       │   │   ├── dashboard_reporting.py
│   │       │   │   └── incident_management.py
│   │       │   ├── health_init.py
│   │       │   ├── health_integrations.py
│   │       │   ├── health_utils.py
│   │       │   └── system_health_agent.py
│   │       └── tests
│   │           ├── README.md
│   │           └── test_system_health_agent.py
│   ├── portfolio-management
│   │   ├── README.md
│   │   ├── business-case-agent
│   │   │   ├── BOUNDARY-NOTES.md
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── business_case_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── analysis_actions.py
│   │   │   │   │   ├── generation_actions.py
│   │   │   │   │   ├── query_actions.py
│   │   │   │   │   └── roi_actions.py
│   │   │   │   ├── business_case_investment_agent.py
│   │   │   │   ├── business_case_models.py
│   │   │   │   └── business_case_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_business_case_investment_agent.py
│   │   ├── demand-intake-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── demand_intake_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── intake_actions.py
│   │   │   │   │   └── pipeline_actions.py
│   │   │   │   ├── demand_intake_agent.py
│   │   │   │   ├── demand_intake_models.py
│   │   │   │   └── demand_intake_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_demand_intake_agent.py
│   │   ├── portfolio-optimisation-agent
│   │   │   ├── Dockerfile
│   │   │   ├── README.md
│   │   │   ├── demo-fixtures
│   │   │   │   └── sample-response.json
│   │   │   ├── src
│   │   │   │   ├── portfolio_actions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── optimization_actions.py
│   │   │   │   │   ├── prioritization_actions.py
│   │   │   │   │   ├── scenario_actions.py
│   │   │   │   │   └── status_actions.py
│   │   │   │   ├── portfolio_models.py
│   │   │   │   ├── portfolio_strategy_agent.py
│   │   │   │   └── portfolio_utils.py
│   │   │   └── tests
│   │   │       ├── README.md
│   │   │       └── test_portfolio_strategy_agent.py
│   │   └── program-management-agent
│   │       ├── Dockerfile
│   │       ├── README.md
│   │       ├── demo-fixtures
│   │       │   └── sample-response.json
│   │       ├── src
│   │       │   ├── program_actions
│   │       │   │   ├── __init__.py
│   │       │   │   ├── aggregate_benefits.py
│   │       │   │   ├── analyze_change_impact.py
│   │       │   │   ├── approval_actions.py
│   │       │   │   ├── coordinate_resources.py
│   │       │   │   ├── create_program.py
│   │       │   │   ├── generate_roadmap.py
│   │       │   │   ├── get_program_health.py
│   │       │   │   ├── identify_synergies.py
│   │       │   │   ├── optimize_program.py
│   │       │   │   └── track_dependencies.py
│   │       │   ├── program_infrastructure.py
│   │       │   ├── program_management_agent.py
│   │       │   ├── program_models.py
│   │       │   └── program_utils.py
│   │       └── tests
│   │           ├── README.md
│   │           └── test_program_management_agent.py
│   └── runtime
│       ├── README.md
│       ├── __init__.py
│       ├── eval
│       │   ├── README.md
│       │   ├── fixtures
│       │   │   ├── definition
│       │   │   │   └── definition-minimal.yaml
│       │   │   ├── flow-intent-router.yaml
│       │   │   ├── flow-orchestration.yaml
│       │   │   └── tools
│       │   │       └── tools-minimal.yaml
│       │   ├── manifest.yaml
│       │   └── run_eval.py
│       ├── prompts
│       │   ├── approval-workflow
│       │   │   └── approval_prompt_v1.md
│       │   ├── intent-router
│       │   │   └── classification_prompt_v1.md
│       │   ├── knowledge-agent
│       │   │   └── summary_prompt_v1.md
│       │   └── response-orchestration
│       │       └── orchestration_prompt_v1.md
│       ├── src
│       │   ├── __init__.py
│       │   ├── agent_catalog.py
│       │   ├── audit.py
│       │   ├── base_agent.py
│       │   ├── data_service.py
│       │   ├── event_bus.py
│       │   ├── execution_events.py
│       │   ├── memory_store.py
│       │   ├── models.py
│       │   ├── notification_service.py
│       │   ├── orchestrator.py
│       │   ├── policy.py
│       │   └── state_store.py
│       └── timeout_harness.py
├── apps
│   ├── README.md
│   ├── admin-console
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── src
│   │   │   ├── admin_store.py
│   │   │   ├── config.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── README.md
│   ├── analytics-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── job_registry.py
│   │   ├── jobs
│   │   │   ├── README.md
│   │   │   ├── manifests
│   │   │   │   └── daily-portfolio-rollup.yaml
│   │   │   └── schema
│   │   │       └── job-manifest.schema.json
│   │   ├── models
│   │   │   └── README.md
│   │   ├── src
│   │   │   ├── config.py
│   │   │   ├── health.py
│   │   │   ├── kpi_engine.py
│   │   │   ├── main.py
│   │   │   ├── metrics_store.py
│   │   │   ├── predictive.py
│   │   │   ├── predictive_models.py
│   │   │   ├── predictive_routes.py
│   │   │   └── scheduler.py
│   │   └── tests
│   │       ├── README.md
│   │       └── test_scheduler.py
│   ├── api-gateway
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── leader-election-configmap.yaml
│   │   │   │   ├── leader-election-rbac.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   ├── secretproviderclass.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   └── serviceaccount.yaml
│   │   │   └── values.yaml
│   │   ├── migrations
│   │   │   └── sql
│   │   │       ├── 001_init_postgresql.sql
│   │   │       └── 001_init_sqlite.sql
│   │   ├── openapi
│   │   │   └── README.md
│   │   ├── src
│   │   │   ├── README.md
│   │   │   └── api
│   │   │       ├── README.md
│   │   │       ├── __init__.py
│   │   │       ├── bootstrap
│   │   │       │   ├── __init__.py
│   │   │       │   ├── components.py
│   │   │       │   ├── connector_component.py
│   │   │       │   ├── document_session_component.py
│   │   │       │   ├── leader_election_component.py
│   │   │       │   ├── orchestrator_component.py
│   │   │       │   ├── registry.py
│   │   │       │   └── secret_rotation_component.py
│   │   │       ├── certification_storage.py
│   │   │       ├── circuit_breaker.py
│   │   │       ├── config.py
│   │   │       ├── connector_loader.py
│   │   │       ├── cors.py
│   │   │       ├── dependencies.py
│   │   │       ├── document_session_store.py
│   │   │       ├── leader_election.py
│   │   │       ├── limiter.py
│   │   │       ├── main.py
│   │   │       ├── middleware
│   │   │       │   ├── __init__.py
│   │   │       │   └── security.py
│   │   │       ├── routes
│   │   │       │   ├── __init__.py
│   │   │       │   ├── admin.py
│   │   │       │   ├── agent_config.py
│   │   │       │   ├── agents.py
│   │   │       │   ├── analytics.py
│   │   │       │   ├── audit.py
│   │   │       │   ├── certifications.py
│   │   │       │   ├── compliance_research.py
│   │   │       │   ├── connectors.py
│   │   │       │   ├── documents.py
│   │   │       │   ├── health.py
│   │   │       │   ├── lineage.py
│   │   │       │   ├── marketplace.py
│   │   │       │   ├── risk_research.py
│   │   │       │   ├── scope_research.py
│   │   │       │   ├── vendor_management.py
│   │   │       │   ├── vendor_research.py
│   │   │       │   └── workflows.py
│   │   │       ├── runtime_bootstrap.py
│   │   │       ├── schemas
│   │   │       │   ├── __init__.py
│   │   │       │   └── certification.schema.json
│   │   │       ├── secret_rotation.py
│   │   │       ├── slowapi_compat.py
│   │   │       └── webhook_storage.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── conftest.py
│   │       ├── test_agents_and_circuit_breaker.py
│   │       ├── test_bootstrap_lifecycle.py
│   │       ├── test_connectors_routes.py
│   │       ├── test_document_session_store_concurrency.py
│   │       ├── test_document_session_store_policy.py
│   │       ├── test_security_middleware.py
│   │       └── test_workflows_routes.py
│   ├── connector-hub
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── registry
│   │   │   └── README.md
│   │   ├── sandbox
│   │   │   ├── README.md
│   │   │   ├── examples
│   │   │   │   └── github-sandbox-connector.yaml
│   │   │   ├── fixtures
│   │   │   │   ├── issues.json
│   │   │   │   └── repo.json
│   │   │   └── schema
│   │   │       └── sandbox-connector.schema.json
│   │   ├── sandbox_registry.py
│   │   ├── src
│   │   │   ├── connector_storage.py
│   │   │   ├── health_aggregator.py
│   │   │   ├── health_models.py
│   │   │   ├── health_routes.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── README.md
│   ├── demo_streamlit
│   │   ├── .streamlit
│   │   │   └── config.toml
│   │   ├── app.py
│   │   ├── data
│   │   │   ├── assistant_outcome_variants.json
│   │   │   └── feature_flags_demo.json
│   │   ├── storage
│   │   │   └── demo_outbox.json
│   │   └── validate_demo.py
│   ├── document-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── document_policy_config.py
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── migrations
│   │   │   └── README.md
│   │   ├── policies
│   │   │   ├── README.md
│   │   │   ├── bundles
│   │   │   │   └── default-policy-bundle.yaml
│   │   │   └── schema
│   │   │       └── policy-bundle.schema.json
│   │   ├── src
│   │   │   ├── briefing_renderer.py
│   │   │   ├── config.py
│   │   │   ├── document_policy.py
│   │   │   ├── document_storage.py
│   │   │   └── main.py
│   │   └── tests
│   │       ├── README.md
│   │       └── test_document_dlp_and_crypto.py
│   ├── mobile
│   │   ├── App.tsx
│   │   ├── README.md
│   │   ├── app.json
│   │   ├── babel.config.js
│   │   ├── jest.config.js
│   │   ├── package.json
│   │   ├── src
│   │   │   ├── README.md
│   │   │   ├── api
│   │   │   │   └── client.ts
│   │   │   ├── components
│   │   │   │   ├── AppErrorBoundary.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── LabelValueRow.tsx
│   │   │   │   ├── Sparkline.tsx
│   │   │   │   └── __tests__
│   │   │   │       └── AppErrorBoundary.test.tsx
│   │   │   ├── context
│   │   │   │   ├── AppContext.tsx
│   │   │   │   └── __tests__
│   │   │   │       └── AppContext.test.tsx
│   │   │   ├── i18n
│   │   │   │   ├── index.tsx
│   │   │   │   └── locales
│   │   │   │       ├── de.json
│   │   │   │       └── en.json
│   │   │   ├── integration
│   │   │   │   └── mobileFlows.integration.test.tsx
│   │   │   ├── screens
│   │   │   │   ├── ApprovalsScreen.tsx
│   │   │   │   ├── AssistantScreen.tsx
│   │   │   │   ├── CanvasScreen.tsx
│   │   │   │   ├── ConnectorsScreen.tsx
│   │   │   │   ├── DashboardScreen.tsx
│   │   │   │   ├── LoginScreen.tsx
│   │   │   │   ├── MethodologiesScreen.tsx
│   │   │   │   ├── StatusUpdatesScreen.tsx
│   │   │   │   └── TenantSelectionScreen.tsx
│   │   │   ├── services
│   │   │   │   ├── approvalQueue.ts
│   │   │   │   ├── biometricAuth.ts
│   │   │   │   ├── notifications.ts
│   │   │   │   ├── secureSession.ts
│   │   │   │   ├── statusQueue.ts
│   │   │   │   └── telemetry.ts
│   │   │   └── theme.ts
│   │   └── tsconfig.json
│   ├── orchestration-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── leader-election-configmap.yaml
│   │   │   │   ├── leader-election-rbac.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   └── serviceaccount.yaml
│   │   │   └── values.yaml
│   │   ├── planners
│   │   │   └── README.md
│   │   ├── policies
│   │   │   ├── README.md
│   │   │   ├── bundles
│   │   │   │   └── default-policy-bundle.yaml
│   │   │   └── schema
│   │   │       └── policy-bundle.schema.json
│   │   ├── src
│   │   │   ├── config.py
│   │   │   ├── leader_election.py
│   │   │   ├── main.py
│   │   │   ├── orchestrator.py
│   │   │   ├── persistence.py
│   │   │   └── workflow_client.py
│   │   ├── storage
│   │   │   └── orchestration-state.json
│   │   └── tests
│   │       └── README.md
│   ├── web
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── data
│   │   │   ├── README.md
│   │   │   ├── agents.json
│   │   │   ├── demo
│   │   │   │   ├── demo_run_log.json
│   │   │   │   └── sor_fixtures.json
│   │   │   ├── demo_conversations
│   │   │   │   ├── deliver_status_report.json
│   │   │   │   ├── design_wbs.json
│   │   │   │   ├── discover_charter.json
│   │   │   │   ├── embed_lessons_learned.json
│   │   │   │   ├── financial_review.json
│   │   │   │   ├── portfolio_review.json
│   │   │   │   ├── project_intake.json
│   │   │   │   ├── resource_request.json
│   │   │   │   ├── risk_review.json
│   │   │   │   ├── stage_gate_approval.json
│   │   │   │   └── vendor_procurement.json
│   │   │   ├── demo_dashboards
│   │   │   │   ├── approvals.json
│   │   │   │   ├── delivery_governance.json
│   │   │   │   ├── executive_portfolio.json
│   │   │   │   ├── lifecycle-metrics.json
│   │   │   │   ├── portfolio-health.json
│   │   │   │   ├── project-dashboard-aggregations.json
│   │   │   │   ├── project-dashboard-health.json
│   │   │   │   ├── project-dashboard-issues.json
│   │   │   │   ├── project-dashboard-kpis.json
│   │   │   │   ├── project-dashboard-narrative.json
│   │   │   │   ├── project-dashboard-quality.json
│   │   │   │   ├── project-dashboard-risks.json
│   │   │   │   ├── project-dashboard-trends.json
│   │   │   │   ├── vendor_procurement_risk.json
│   │   │   │   └── workflow-monitoring.json
│   │   │   ├── demo_seed.json
│   │   │   ├── knowledge.db
│   │   │   ├── llm_models.json
│   │   │   ├── merge_review_seed.json
│   │   │   ├── methodology_node_runtime.json
│   │   │   ├── ppm.db
│   │   │   ├── projects.json
│   │   │   ├── requirements.json
│   │   │   ├── roles.json
│   │   │   ├── seed.json
│   │   │   ├── template_mappings.json
│   │   │   ├── templates.json
│   │   │   └── workflows
│   │   │       ├── change_request.json
│   │   │       └── intake_to_delivery.json
│   │   ├── e2e
│   │   │   └── README.md
│   │   ├── frontend
│   │   │   ├── .eslintrc.cjs
│   │   │   ├── .gitignore
│   │   │   ├── .storybook
│   │   │   │   ├── main.ts
│   │   │   │   ├── preview.ts
│   │   │   │   └── test-runner.ts
│   │   │   ├── README.md
│   │   │   ├── index.html
│   │   │   ├── package-lock.json
│   │   │   ├── package.json
│   │   │   ├── public
│   │   │   │   └── favicon.svg
│   │   │   ├── scripts
│   │   │   │   ├── check-design-tokens.mjs
│   │   │   │   ├── check-raw-json-casts.mjs
│   │   │   │   ├── generate-css-module-types.mjs
│   │   │   │   └── raw-json-cast-allowlist.txt
│   │   │   ├── src
│   │   │   │   ├── App.demo.test.tsx
│   │   │   │   ├── App.module.css
│   │   │   │   ├── App.module.css.d.ts
│   │   │   │   ├── App.tsx
│   │   │   │   ├── README.md
│   │   │   │   ├── auth
│   │   │   │   │   └── permissions.ts
│   │   │   │   ├── components
│   │   │   │   │   ├── agentConfig
│   │   │   │   │   │   ├── AgentGallery.module.css
│   │   │   │   │   │   ├── AgentGallery.module.css.d.ts
│   │   │   │   │   │   ├── AgentGallery.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── agentRuns
│   │   │   │   │   │   ├── AgentRunDetail.module.css
│   │   │   │   │   │   ├── AgentRunDetail.module.css.d.ts
│   │   │   │   │   │   ├── AgentRunDetail.tsx
│   │   │   │   │   │   ├── AgentRunList.module.css
│   │   │   │   │   │   ├── AgentRunList.module.css.d.ts
│   │   │   │   │   │   ├── AgentRunList.tsx
│   │   │   │   │   │   ├── ProgressBadge.module.css
│   │   │   │   │   │   ├── ProgressBadge.module.css.d.ts
│   │   │   │   │   │   └── ProgressBadge.tsx
│   │   │   │   │   ├── analytics
│   │   │   │   │   │   ├── ScenarioBuilder.module.css
│   │   │   │   │   │   ├── ScenarioBuilder.module.css.d.ts
│   │   │   │   │   │   └── ScenarioBuilder.tsx
│   │   │   │   │   ├── assistant
│   │   │   │   │   │   ├── ActionChipButton.module.css
│   │   │   │   │   │   ├── ActionChipButton.module.css.d.ts
│   │   │   │   │   │   ├── ActionChipButton.tsx
│   │   │   │   │   │   ├── AgentActivityPanel.module.css
│   │   │   │   │   │   ├── AgentActivityPanel.module.css.d.ts
│   │   │   │   │   │   ├── AgentActivityPanel.tsx
│   │   │   │   │   │   ├── AssistantHeader.module.css
│   │   │   │   │   │   ├── AssistantHeader.module.css.d.ts
│   │   │   │   │   │   ├── AssistantHeader.tsx
│   │   │   │   │   │   ├── AssistantPanel.demo.test.tsx
│   │   │   │   │   │   ├── AssistantPanel.module.css
│   │   │   │   │   │   ├── AssistantPanel.module.css.d.ts
│   │   │   │   │   │   ├── AssistantPanel.test.tsx
│   │   │   │   │   │   ├── AssistantPanel.tsx
│   │   │   │   │   │   ├── ChatInput.module.css
│   │   │   │   │   │   ├── ChatInput.module.css.d.ts
│   │   │   │   │   │   ├── ChatInput.test.tsx
│   │   │   │   │   │   ├── ChatInput.tsx
│   │   │   │   │   │   ├── ContextBar.module.css
│   │   │   │   │   │   ├── ContextBar.module.css.d.ts
│   │   │   │   │   │   ├── ContextBar.test.tsx
│   │   │   │   │   │   ├── ContextBar.tsx
│   │   │   │   │   │   ├── ConversationalCommandCard.module.css
│   │   │   │   │   │   ├── ConversationalCommandCard.module.css.d.ts
│   │   │   │   │   │   ├── ConversationalCommandCard.tsx
│   │   │   │   │   │   ├── MessageBubble.module.css
│   │   │   │   │   │   ├── MessageBubble.module.css.d.ts
│   │   │   │   │   │   ├── MessageBubble.tsx
│   │   │   │   │   │   ├── MessageList.module.css
│   │   │   │   │   │   ├── MessageList.module.css.d.ts
│   │   │   │   │   │   ├── MessageList.test.tsx
│   │   │   │   │   │   ├── MessageList.tsx
│   │   │   │   │   │   ├── PromptPicker.module.css
│   │   │   │   │   │   ├── PromptPicker.module.css.d.ts
│   │   │   │   │   │   ├── PromptPicker.tsx
│   │   │   │   │   │   ├── QuickActions.module.css
│   │   │   │   │   │   ├── QuickActions.module.css.d.ts
│   │   │   │   │   │   ├── QuickActions.test.tsx
│   │   │   │   │   │   ├── QuickActions.tsx
│   │   │   │   │   │   ├── ScopeResearchCard.module.css
│   │   │   │   │   │   ├── ScopeResearchCard.module.css.d.ts
│   │   │   │   │   │   ├── ScopeResearchCard.tsx
│   │   │   │   │   │   ├── assistantMode.test.ts
│   │   │   │   │   │   ├── assistantMode.ts
│   │   │   │   │   │   ├── entryQuickActions.ts
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── canvas
│   │   │   │   │   │   ├── AgentAnnotationOverlay.module.css
│   │   │   │   │   │   ├── AgentAnnotationOverlay.module.css.d.ts
│   │   │   │   │   │   ├── AgentAnnotationOverlay.tsx
│   │   │   │   │   │   ├── CanvasWorkspace.module.css
│   │   │   │   │   │   ├── CanvasWorkspace.module.css.d.ts
│   │   │   │   │   │   ├── CanvasWorkspace.tsx
│   │   │   │   │   │   ├── NewCanvasTypes.smoke.test.tsx
│   │   │   │   │   │   ├── PresenceIndicators.module.css
│   │   │   │   │   │   ├── PresenceIndicators.module.css.d.ts
│   │   │   │   │   │   ├── PresenceIndicators.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── collections
│   │   │   │   │   │   ├── BulkActions.module.css
│   │   │   │   │   │   ├── BulkActions.module.css.d.ts
│   │   │   │   │   │   ├── BulkActions.tsx
│   │   │   │   │   │   ├── EntityTable.module.css
│   │   │   │   │   │   ├── EntityTable.module.css.d.ts
│   │   │   │   │   │   ├── EntityTable.tsx
│   │   │   │   │   │   ├── FacetedFilter.module.css
│   │   │   │   │   │   ├── FacetedFilter.module.css.d.ts
│   │   │   │   │   │   └── FacetedFilter.tsx
│   │   │   │   │   ├── config
│   │   │   │   │   │   ├── ConfigForm.module.css
│   │   │   │   │   │   ├── ConfigForm.module.css.d.ts
│   │   │   │   │   │   ├── ConfigForm.test.tsx
│   │   │   │   │   │   ├── ConfigForm.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── connectors
│   │   │   │   │   │   ├── CategorySection.tsx
│   │   │   │   │   │   ├── CertificationModal.tsx
│   │   │   │   │   │   ├── ConnectorCard.tsx
│   │   │   │   │   │   ├── ConnectorConfigModal.tsx
│   │   │   │   │   │   ├── ConnectorGallery.module.css
│   │   │   │   │   │   ├── ConnectorGallery.module.css.d.ts
│   │   │   │   │   │   ├── ConnectorGallery.test.tsx
│   │   │   │   │   │   ├── ConnectorGallery.tsx
│   │   │   │   │   │   ├── ConnectorIcon.tsx
│   │   │   │   │   │   ├── ConnectorSearchFilters.tsx
│   │   │   │   │   │   ├── SyncStatusPanel.module.css
│   │   │   │   │   │   ├── SyncStatusPanel.module.css.d.ts
│   │   │   │   │   │   ├── SyncStatusPanel.tsx
│   │   │   │   │   │   ├── connectorGalleryTypes.ts
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── dashboard
│   │   │   │   │   │   ├── HealthBadge.module.css
│   │   │   │   │   │   ├── HealthBadge.module.css.d.ts
│   │   │   │   │   │   ├── HealthBadge.tsx
│   │   │   │   │   │   ├── KpiWidget.module.css
│   │   │   │   │   │   ├── KpiWidget.module.css.d.ts
│   │   │   │   │   │   ├── KpiWidget.tsx
│   │   │   │   │   │   ├── StatusIndicator.module.css
│   │   │   │   │   │   ├── StatusIndicator.module.css.d.ts
│   │   │   │   │   │   └── StatusIndicator.tsx
│   │   │   │   │   ├── docs
│   │   │   │   │   │   ├── CoeditEditor.module.css
│   │   │   │   │   │   ├── CoeditEditor.module.css.d.ts
│   │   │   │   │   │   └── CoeditEditor.tsx
│   │   │   │   │   ├── icon
│   │   │   │   │   │   ├── Icon.module.css
│   │   │   │   │   │   ├── Icon.module.css.d.ts
│   │   │   │   │   │   ├── Icon.tsx
│   │   │   │   │   │   └── iconMap.ts
│   │   │   │   │   ├── intake
│   │   │   │   │   │   ├── AutoClassificationBadge.module.css
│   │   │   │   │   │   ├── AutoClassificationBadge.module.css.d.ts
│   │   │   │   │   │   ├── AutoClassificationBadge.tsx
│   │   │   │   │   │   ├── DuplicateDetectionPanel.module.css
│   │   │   │   │   │   ├── DuplicateDetectionPanel.module.css.d.ts
│   │   │   │   │   │   └── DuplicateDetectionPanel.tsx
│   │   │   │   │   ├── knowledge
│   │   │   │   │   │   ├── RecommendationSidebar.module.css
│   │   │   │   │   │   ├── RecommendationSidebar.module.css.d.ts
│   │   │   │   │   │   └── RecommendationSidebar.tsx
│   │   │   │   │   ├── layout
│   │   │   │   │   │   ├── AppLayout.module.css
│   │   │   │   │   │   ├── AppLayout.module.css.d.ts
│   │   │   │   │   │   ├── AppLayout.test.tsx
│   │   │   │   │   │   ├── AppLayout.tsx
│   │   │   │   │   │   ├── Header.module.css
│   │   │   │   │   │   ├── Header.module.css.d.ts
│   │   │   │   │   │   ├── Header.tsx
│   │   │   │   │   │   ├── LeftPanel.module.css
│   │   │   │   │   │   ├── LeftPanel.module.css.d.ts
│   │   │   │   │   │   ├── LeftPanel.test.tsx
│   │   │   │   │   │   ├── LeftPanel.tsx
│   │   │   │   │   │   ├── MainCanvas.module.css
│   │   │   │   │   │   ├── MainCanvas.module.css.d.ts
│   │   │   │   │   │   ├── MainCanvas.tsx
│   │   │   │   │   │   ├── SearchOverlay.module.css
│   │   │   │   │   │   ├── SearchOverlay.module.css.d.ts
│   │   │   │   │   │   ├── SearchOverlay.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── methodology
│   │   │   │   │   │   ├── ActivityDetailPanel.test.tsx
│   │   │   │   │   │   ├── ActivityDetailPanel.tsx
│   │   │   │   │   │   ├── MethodologyMapCanvas.module.css
│   │   │   │   │   │   ├── MethodologyMapCanvas.module.css.d.ts
│   │   │   │   │   │   ├── MethodologyMapCanvas.test.tsx
│   │   │   │   │   │   ├── MethodologyMapCanvas.tsx
│   │   │   │   │   │   ├── MethodologyNav.module.css
│   │   │   │   │   │   ├── MethodologyNav.module.css.d.ts
│   │   │   │   │   │   ├── MethodologyNav.test.tsx
│   │   │   │   │   │   ├── MethodologyNav.tsx
│   │   │   │   │   │   ├── MethodologyWorkspaceSurface.test.ts
│   │   │   │   │   │   ├── MethodologyWorkspaceSurface.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── onboarding
│   │   │   │   │   │   ├── OnboardingTour.module.css
│   │   │   │   │   │   ├── OnboardingTour.module.css.d.ts
│   │   │   │   │   │   ├── OnboardingTour.tsx
│   │   │   │   │   │   └── onboardingMessages.ts
│   │   │   │   │   ├── project
│   │   │   │   │   │   ├── AgentGallery.module.css
│   │   │   │   │   │   ├── AgentGallery.module.css.d.ts
│   │   │   │   │   │   ├── AgentGallery.tsx
│   │   │   │   │   │   ├── CertificationModal.tsx
│   │   │   │   │   │   ├── ConnectorCard.tsx
│   │   │   │   │   │   ├── ConnectorCategorySection.tsx
│   │   │   │   │   │   ├── ConnectorConfigModal.tsx
│   │   │   │   │   │   ├── ConnectorFilterBar.tsx
│   │   │   │   │   │   ├── ConnectorIcon.tsx
│   │   │   │   │   │   ├── McpProjectConfigSection.tsx
│   │   │   │   │   │   ├── ProjectConfigSection.module.css
│   │   │   │   │   │   ├── ProjectConfigSection.module.css.d.ts
│   │   │   │   │   │   ├── ProjectConfigSection.tsx
│   │   │   │   │   │   ├── ProjectConnectorGallery.tsx
│   │   │   │   │   │   ├── ProjectMcpSidebar.module.css
│   │   │   │   │   │   ├── ProjectMcpSidebar.module.css.d.ts
│   │   │   │   │   │   ├── ProjectMcpSidebar.tsx
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   └── projectConnectorTypes.ts
│   │   │   │   │   ├── security
│   │   │   │   │   │   ├── ClassificationBadge.module.css
│   │   │   │   │   │   ├── ClassificationBadge.module.css.d.ts
│   │   │   │   │   │   ├── ClassificationBadge.tsx
│   │   │   │   │   │   ├── PolicyEditor.module.css
│   │   │   │   │   │   ├── PolicyEditor.module.css.d.ts
│   │   │   │   │   │   └── PolicyEditor.tsx
│   │   │   │   │   ├── templates
│   │   │   │   │   │   ├── TemplateGallery.module.css
│   │   │   │   │   │   ├── TemplateGallery.module.css.d.ts
│   │   │   │   │   │   ├── TemplateGallery.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── theme
│   │   │   │   │   │   └── ThemeProvider.tsx
│   │   │   │   │   ├── tours
│   │   │   │   │   │   ├── TourProvider.module.css
│   │   │   │   │   │   ├── TourProvider.module.css.d.ts
│   │   │   │   │   │   ├── TourProvider.test.tsx
│   │   │   │   │   │   ├── TourProvider.tsx
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── ui
│   │   │   │   │   │   ├── ConfirmDialog.module.css
│   │   │   │   │   │   ├── ConfirmDialog.module.css.d.ts
│   │   │   │   │   │   ├── ConfirmDialog.tsx
│   │   │   │   │   │   ├── EmptyState.module.css
│   │   │   │   │   │   ├── EmptyState.module.css.d.ts
│   │   │   │   │   │   ├── EmptyState.tsx
│   │   │   │   │   │   ├── ErrorBoundary.test.tsx
│   │   │   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   │   │   ├── FadeIn.module.css
│   │   │   │   │   │   ├── FadeIn.module.css.d.ts
│   │   │   │   │   │   ├── FadeIn.tsx
│   │   │   │   │   │   ├── FocusTrap.tsx
│   │   │   │   │   │   ├── Skeleton.module.css
│   │   │   │   │   │   ├── Skeleton.module.css.d.ts
│   │   │   │   │   │   └── Skeleton.tsx
│   │   │   │   │   └── workflow
│   │   │   │   │       ├── NLWorkflowInput.module.css
│   │   │   │   │       ├── NLWorkflowInput.module.css.d.ts
│   │   │   │   │       └── NLWorkflowInput.tsx
│   │   │   │   ├── e2e
│   │   │   │   │   ├── criticalJourneys.test.tsx
│   │   │   │   │   └── intakeAssistantRegression.test.tsx
│   │   │   │   ├── hooks
│   │   │   │   │   ├── assistant
│   │   │   │   │   │   ├── useAssistantChat.ts
│   │   │   │   │   │   ├── useContextSync.ts
│   │   │   │   │   │   ├── useCopilotStream.ts
│   │   │   │   │   │   ├── useIntakeAssistantAdapter.ts
│   │   │   │   │   │   └── useSuggestionEngine.ts
│   │   │   │   │   ├── useRealtimeConsole.ts
│   │   │   │   │   └── useRequestState.ts
│   │   │   │   ├── i18n
│   │   │   │   │   ├── index.tsx
│   │   │   │   │   └── locales
│   │   │   │   │       ├── de.json
│   │   │   │   │       ├── en.json
│   │   │   │   │       └── pseudo.json
│   │   │   │   ├── main.tsx
│   │   │   │   ├── pages
│   │   │   │   │   ├── AgentMarketplacePage.module.css
│   │   │   │   │   ├── AgentMarketplacePage.module.css.d.ts
│   │   │   │   │   ├── AgentMarketplacePage.tsx
│   │   │   │   │   ├── AgentProfilePage.module.css
│   │   │   │   │   ├── AgentProfilePage.module.css.d.ts
│   │   │   │   │   ├── AgentProfilePage.test.tsx
│   │   │   │   │   ├── AgentProfilePage.tsx
│   │   │   │   │   ├── AgentRunsPage.module.css
│   │   │   │   │   ├── AgentRunsPage.module.css.d.ts
│   │   │   │   │   ├── AgentRunsPage.tsx
│   │   │   │   │   ├── AnalyticsDashboard.module.css
│   │   │   │   │   ├── AnalyticsDashboard.module.css.d.ts
│   │   │   │   │   ├── AnalyticsDashboard.tsx
│   │   │   │   │   ├── ApprovalsPage.module.css
│   │   │   │   │   ├── ApprovalsPage.module.css.d.ts
│   │   │   │   │   ├── ApprovalsPage.tsx
│   │   │   │   │   ├── AuditLogPage.module.css
│   │   │   │   │   ├── AuditLogPage.module.css.d.ts
│   │   │   │   │   ├── AuditLogPage.tsx
│   │   │   │   │   ├── CapacityPlanningPage.module.css
│   │   │   │   │   ├── CapacityPlanningPage.module.css.d.ts
│   │   │   │   │   ├── CapacityPlanningPage.tsx
│   │   │   │   │   ├── ConfigPage.module.css
│   │   │   │   │   ├── ConfigPage.module.css.d.ts
│   │   │   │   │   ├── ConfigPage.test.tsx
│   │   │   │   │   ├── ConfigPage.tsx
│   │   │   │   │   ├── ConnectorDetailPage.module.css
│   │   │   │   │   ├── ConnectorDetailPage.module.css.d.ts
│   │   │   │   │   ├── ConnectorDetailPage.tsx
│   │   │   │   │   ├── ConnectorHealthDashboardPage.module.css
│   │   │   │   │   ├── ConnectorHealthDashboardPage.module.css.d.ts
│   │   │   │   │   ├── ConnectorHealthDashboardPage.tsx
│   │   │   │   │   ├── ConnectorMarketplacePage.tsx
│   │   │   │   │   ├── DemoRunPage.module.css
│   │   │   │   │   ├── DemoRunPage.module.css.d.ts
│   │   │   │   │   ├── DemoRunPage.tsx
│   │   │   │   │   ├── DocumentSearchPage.module.css
│   │   │   │   │   ├── DocumentSearchPage.module.css.d.ts
│   │   │   │   │   ├── DocumentSearchPage.tsx
│   │   │   │   │   ├── EnterpriseUpliftPage.test.tsx
│   │   │   │   │   ├── EnterpriseUpliftPage.tsx
│   │   │   │   │   ├── ExecutiveBriefingPage.module.css
│   │   │   │   │   ├── ExecutiveBriefingPage.module.css.d.ts
│   │   │   │   │   ├── ExecutiveBriefingPage.tsx
│   │   │   │   │   ├── ForbiddenPage.module.css
│   │   │   │   │   ├── ForbiddenPage.module.css.d.ts
│   │   │   │   │   ├── ForbiddenPage.tsx
│   │   │   │   │   ├── GlobalSearch.module.css
│   │   │   │   │   ├── GlobalSearch.module.css.d.ts
│   │   │   │   │   ├── GlobalSearch.security.test.tsx
│   │   │   │   │   ├── GlobalSearch.tsx
│   │   │   │   │   ├── HomePage.module.css
│   │   │   │   │   ├── HomePage.module.css.d.ts
│   │   │   │   │   ├── HomePage.tsx
│   │   │   │   │   ├── IntakeApprovalsPage.module.css
│   │   │   │   │   ├── IntakeApprovalsPage.module.css.d.ts
│   │   │   │   │   ├── IntakeApprovalsPage.tsx
│   │   │   │   │   ├── IntakeFormPage.module.css
│   │   │   │   │   ├── IntakeFormPage.module.css.d.ts
│   │   │   │   │   ├── IntakeFormPage.test.tsx
│   │   │   │   │   ├── IntakeFormPage.tsx
│   │   │   │   │   ├── IntakeStatusPage.module.css
│   │   │   │   │   ├── IntakeStatusPage.module.css.d.ts
│   │   │   │   │   ├── IntakeStatusPage.tsx
│   │   │   │   │   ├── KnowledgeGraphPage.module.css
│   │   │   │   │   ├── KnowledgeGraphPage.module.css.d.ts
│   │   │   │   │   ├── KnowledgeGraphPage.tsx
│   │   │   │   │   ├── LessonsLearnedPage.module.css
│   │   │   │   │   ├── LessonsLearnedPage.module.css.d.ts
│   │   │   │   │   ├── LessonsLearnedPage.tsx
│   │   │   │   │   ├── LoginPage.module.css
│   │   │   │   │   ├── LoginPage.module.css.d.ts
│   │   │   │   │   ├── LoginPage.tsx
│   │   │   │   │   ├── MergeReviewPage.module.css
│   │   │   │   │   ├── MergeReviewPage.module.css.d.ts
│   │   │   │   │   ├── MergeReviewPage.tsx
│   │   │   │   │   ├── MethodologyEditor.module.css
│   │   │   │   │   ├── MethodologyEditor.module.css.d.ts
│   │   │   │   │   ├── MethodologyEditor.test.tsx
│   │   │   │   │   ├── MethodologyEditor.tsx
│   │   │   │   │   ├── NotificationCenterPage.module.css
│   │   │   │   │   ├── NotificationCenterPage.module.css.d.ts
│   │   │   │   │   ├── NotificationCenterPage.tsx
│   │   │   │   │   ├── OrganisationMethodologySettings.tsx
│   │   │   │   │   ├── PerformanceDashboardPage.module.css
│   │   │   │   │   ├── PerformanceDashboardPage.module.css.d.ts
│   │   │   │   │   ├── PerformanceDashboardPage.tsx
│   │   │   │   │   ├── PredictiveDashboardPage.module.css
│   │   │   │   │   ├── PredictiveDashboardPage.module.css.d.ts
│   │   │   │   │   ├── PredictiveDashboardPage.tsx
│   │   │   │   │   ├── ProjectConfigPage.tsx
│   │   │   │   │   ├── ProjectSetupWizardPage.module.css
│   │   │   │   │   ├── ProjectSetupWizardPage.module.css.d.ts
│   │   │   │   │   ├── ProjectSetupWizardPage.tsx
│   │   │   │   │   ├── PromptManager.module.css
│   │   │   │   │   ├── PromptManager.module.css.d.ts
│   │   │   │   │   ├── PromptManager.tsx
│   │   │   │   │   ├── RoleManager.module.css
│   │   │   │   │   ├── RoleManager.module.css.d.ts
│   │   │   │   │   ├── RoleManager.test.tsx
│   │   │   │   │   ├── RoleManager.tsx
│   │   │   │   │   ├── ScenarioAnalysisPage.tsx
│   │   │   │   │   ├── SecurityPostureDashboardPage.module.css
│   │   │   │   │   ├── SecurityPostureDashboardPage.module.css.d.ts
│   │   │   │   │   ├── SecurityPostureDashboardPage.tsx
│   │   │   │   │   ├── WorkflowDesigner.module.css
│   │   │   │   │   ├── WorkflowDesigner.module.css.d.ts
│   │   │   │   │   ├── WorkflowDesigner.test.tsx
│   │   │   │   │   ├── WorkflowDesigner.tsx
│   │   │   │   │   ├── WorkflowMonitoringPage.module.css
│   │   │   │   │   ├── WorkflowMonitoringPage.module.css.d.ts
│   │   │   │   │   ├── WorkflowMonitoringPage.tsx
│   │   │   │   │   ├── WorkspaceDirectoryPage.module.css
│   │   │   │   │   ├── WorkspaceDirectoryPage.module.css.d.ts
│   │   │   │   │   ├── WorkspaceDirectoryPage.tsx
│   │   │   │   │   ├── WorkspacePage.module.css
│   │   │   │   │   ├── WorkspacePage.module.css.d.ts
│   │   │   │   │   ├── WorkspacePage.test.tsx
│   │   │   │   │   ├── WorkspacePage.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── routing
│   │   │   │   │   ├── RouteGuards.test.tsx
│   │   │   │   │   └── RouteGuards.tsx
│   │   │   │   ├── services
│   │   │   │   │   ├── apiClient.ts
│   │   │   │   │   ├── knowledgeApi.ts
│   │   │   │   │   ├── scheduleApi.ts
│   │   │   │   │   └── searchApi.ts
│   │   │   │   ├── store
│   │   │   │   │   ├── agentConfig
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   ├── types.ts
│   │   │   │   │   │   ├── useAgentConfigStore.test.ts
│   │   │   │   │   │   └── useAgentConfigStore.ts
│   │   │   │   │   ├── assistant
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   ├── types.ts
│   │   │   │   │   │   ├── useAssistantStore.ts
│   │   │   │   │   │   └── useIntakeAssistantStore.ts
│   │   │   │   │   ├── connectors
│   │   │   │   │   │   ├── connectorConnectionSlice.ts
│   │   │   │   │   │   ├── connectorFilterSlice.ts
│   │   │   │   │   │   ├── connectorHelpers.ts
│   │   │   │   │   │   ├── connectorListSlice.ts
│   │   │   │   │   │   ├── connectorModalSlice.ts
│   │   │   │   │   │   ├── connectorStoreTypes.ts
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   ├── types.ts
│   │   │   │   │   │   ├── useConnectorStore.test.ts
│   │   │   │   │   │   └── useConnectorStore.ts
│   │   │   │   │   ├── copilot
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   └── useCopilotStore.ts
│   │   │   │   │   ├── documents
│   │   │   │   │   │   ├── coeditStore.ts
│   │   │   │   │   │   └── index.ts
│   │   │   │   │   ├── index.ts
│   │   │   │   │   ├── methodology
│   │   │   │   │   │   ├── demoData.ts
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   ├── types.ts
│   │   │   │   │   │   ├── useMethodologyStore.demo.test.ts
│   │   │   │   │   │   ├── useMethodologyStore.test.ts
│   │   │   │   │   │   └── useMethodologyStore.ts
│   │   │   │   │   ├── prompts
│   │   │   │   │   │   ├── defaultPrompts.ts
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   └── usePromptStore.ts
│   │   │   │   │   ├── realtime
│   │   │   │   │   │   └── useRealtimeStore.ts
│   │   │   │   │   ├── types.ts
│   │   │   │   │   ├── useAppStore.test.ts
│   │   │   │   │   ├── useAppStore.ts
│   │   │   │   │   ├── useCanvasStore.test.ts
│   │   │   │   │   └── useCanvasStore.ts
│   │   │   │   ├── styles
│   │   │   │   │   ├── index.css
│   │   │   │   │   └── tokens.css
│   │   │   │   ├── test
│   │   │   │   │   ├── accessibility.test.ts
│   │   │   │   │   ├── assistantResponses.test.ts
│   │   │   │   │   ├── prompts.test.ts
│   │   │   │   │   ├── searchApi.test.ts
│   │   │   │   │   ├── setup.ts
│   │   │   │   │   └── tokenContrast.test.ts
│   │   │   │   ├── types
│   │   │   │   │   ├── agentRuns.ts
│   │   │   │   │   ├── css-modules.d.ts
│   │   │   │   │   ├── css-modules.typecheck.ts
│   │   │   │   │   └── prompt.ts
│   │   │   │   ├── utils
│   │   │   │   │   ├── apiValidation.ts
│   │   │   │   │   ├── assistantResponses.ts
│   │   │   │   │   ├── prompts.ts
│   │   │   │   │   └── schema.ts
│   │   │   │   └── vite-env.d.ts
│   │   │   ├── tsconfig.css-modules.json
│   │   │   ├── tsconfig.json
│   │   │   ├── tsconfig.node.json
│   │   │   ├── vite.config.ts
│   │   │   └── vitest.config.ts
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── public
│   │   │   └── README.md
│   │   ├── requirements.txt
│   │   ├── scripts
│   │   │   ├── check_legacy_workspace_artifacts.py
│   │   │   ├── generate_metadata.py
│   │   │   └── legacy_workspace_guard_allowlist.txt
│   │   ├── src
│   │   │   ├── README.md
│   │   │   ├── agent_registry.py
│   │   │   ├── agent_settings_models.py
│   │   │   ├── agent_settings_store.py
│   │   │   ├── analytics_proxy.py
│   │   │   ├── bootstrap.py
│   │   │   ├── canonical_template_registry.py
│   │   │   ├── config.py
│   │   │   ├── connector_hub_proxy.py
│   │   │   ├── data_service_proxy.py
│   │   │   ├── demo_integrations.py
│   │   │   ├── demo_seed.py
│   │   │   ├── dependencies.py
│   │   │   ├── document_proxy.py
│   │   │   ├── gating.py
│   │   │   ├── intake_models.py
│   │   │   ├── intake_store.py
│   │   │   ├── knowledge_store.py
│   │   │   ├── legacy_main.py
│   │   │   ├── lineage_proxy.py
│   │   │   ├── llm_preferences_store.py
│   │   │   ├── main.py
│   │   │   ├── merge_review_models.py
│   │   │   ├── merge_review_store.py
│   │   │   ├── methodologies.py
│   │   │   ├── methodology_node_runtime.py
│   │   │   ├── middleware.py
│   │   │   ├── oidc_client.py
│   │   │   ├── orchestrator_proxy.py
│   │   │   ├── pipeline_models.py
│   │   │   ├── pipeline_store.py
│   │   │   ├── routes
│   │   │   │   ├── __init__.py
│   │   │   │   ├── _deps.py
│   │   │   │   ├── _llm_helpers.py
│   │   │   │   ├── _models.py
│   │   │   │   ├── agent_runs.py
│   │   │   │   ├── agents.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── assistant.py
│   │   │   │   ├── assistant_api.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── briefings.py
│   │   │   │   ├── capacity.py
│   │   │   │   ├── connectors.py
│   │   │   │   ├── copilot_stream.py
│   │   │   │   ├── dashboards.py
│   │   │   │   ├── document_canvas.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── enterprise.py
│   │   │   │   ├── health.py
│   │   │   │   ├── intake.py
│   │   │   │   ├── intake_intelligence.py
│   │   │   │   ├── knowledge.py
│   │   │   │   ├── knowledge_graph.py
│   │   │   │   ├── legacy_pages.py
│   │   │   │   ├── llm.py
│   │   │   │   ├── methodology.py
│   │   │   │   ├── pipeline.py
│   │   │   │   ├── project_setup.py
│   │   │   │   ├── roles.py
│   │   │   │   ├── scenarios.py
│   │   │   │   ├── search.py
│   │   │   │   ├── security_posture.py
│   │   │   │   ├── spreadsheets.py
│   │   │   │   ├── templates_api.py
│   │   │   │   ├── timeline.py
│   │   │   │   ├── tree.py
│   │   │   │   ├── wbs_schedule.py
│   │   │   │   ├── workflow.py
│   │   │   │   ├── workflows_api.py
│   │   │   │   ├── workspace.py
│   │   │   │   └── workspace_state.py
│   │   │   ├── runtime_lifecycle_store.py
│   │   │   ├── search_service.py
│   │   │   ├── spreadsheet_models.py
│   │   │   ├── spreadsheet_store.py
│   │   │   ├── template_mappings.py
│   │   │   ├── template_models.py
│   │   │   ├── template_registry.py
│   │   │   ├── timeline_models.py
│   │   │   ├── timeline_store.py
│   │   │   ├── tree_models.py
│   │   │   ├── tree_store.py
│   │   │   ├── web_services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── assistant.py
│   │   │   │   ├── connectors.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── workflow.py
│   │   │   │   └── workspace.py
│   │   │   ├── workflow_models.py
│   │   │   ├── workflow_store.py
│   │   │   ├── workspace_state.py
│   │   │   └── workspace_state_store.py
│   │   ├── static
│   │   │   ├── index.html
│   │   │   └── styles.css
│   │   ├── storage
│   │   │   ├── agile_backlog.json
│   │   │   ├── agile_metrics.json
│   │   │   ├── agile_pi.json
│   │   │   ├── alerts.json
│   │   │   ├── automations.json
│   │   │   ├── board_configs.json
│   │   │   ├── capacity.json
│   │   │   ├── comments.json
│   │   │   ├── demand.json
│   │   │   ├── finance_actuals.json
│   │   │   ├── finance_budget.json
│   │   │   ├── finance_change_requests.json
│   │   │   ├── finance_forecast.json
│   │   │   ├── llm_preferences.json
│   │   │   ├── merge_review_cases.json
│   │   │   ├── notifications.json
│   │   │   ├── packs.json
│   │   │   ├── prioritisation.json
│   │   │   ├── roles.json
│   │   │   ├── scenarios.json
│   │   │   └── sync_center.json
│   │   └── tests
│   │       ├── README.md
│   │       ├── test_agent_gallery.py
│   │       ├── test_architecture_guards.py
│   │       ├── test_assistant_panel.py
│   │       ├── test_assistant_suggestions.py
│   │       ├── test_connector_gallery_proxy.py
│   │       ├── test_dashboard_canvas_proxy.py
│   │       ├── test_dashboard_canvas_rendering.py
│   │       ├── test_demo_auto_auth.py
│   │       ├── test_demo_mode.py
│   │       ├── test_demo_seed_startup.py
│   │       ├── test_document_canvas_proxy.py
│   │       ├── test_enterprise_uplift_api.py
│   │       ├── test_intake_assistant_api.py
│   │       ├── test_llm_preferences_api.py
│   │       ├── test_methodology_config_validation.py
│   │       ├── test_methodology_gating.py
│   │       ├── test_methodology_node_runtime.py
│   │       ├── test_oidc_login_flow.py
│   │       ├── test_orchestrator_proxy.py
│   │       ├── test_portfolio_lifecycle_endpoints.py
│   │       ├── test_program_views_api.py
│   │       ├── test_program_views_canvas.py
│   │       ├── test_router_contract_analytics.py
│   │       ├── test_router_contract_assistant.py
│   │       ├── test_router_contract_connectors.py
│   │       ├── test_router_contract_documents.py
│   │       ├── test_router_contract_workflow.py
│   │       ├── test_router_contract_workspace.py
│   │       ├── test_search_assistant_api.py
│   │       ├── test_spreadsheet_canvas.py
│   │       ├── test_template_gallery.py
│   │       ├── test_template_mappings.py
│   │       ├── test_template_models.py
│   │       ├── test_timeline_canvas.py
│   │       ├── test_tree_canvas.py
│   │       ├── test_wbs_schedule_api.py
│   │       ├── test_wbs_timeline_canvas.py
│   │       ├── test_workspace_shell.py
│   │       └── test_workspace_state_api.py
│   └── workflow-service
│       ├── .dockerignore
│       ├── Dockerfile
│       ├── README.md
│       ├── helm
│       │   ├── Chart.yaml
│       │   ├── README.md
│       │   ├── templates
│       │   │   ├── _helpers.tpl
│       │   │   ├── broker-rabbitmq.yaml
│       │   │   ├── broker-redis.yaml
│       │   │   ├── celery-worker-deployment.yaml
│       │   │   ├── certificate.yaml
│       │   │   ├── configmap.yaml
│       │   │   ├── deployment.yaml
│       │   │   ├── hpa.yaml
│       │   │   ├── ingress.yaml
│       │   │   ├── pdb.yaml
│       │   │   └── service.yaml
│       │   └── values.yaml
│       ├── migrations
│       │   ├── README.md
│       │   └── sql
│       │       ├── 001_init_postgresql.sql
│       │       └── 001_init_sqlite.sql
│       ├── requirements.txt
│       ├── src
│       │   ├── agent_client.py
│       │   ├── circuit_breaker.py
│       │   ├── config.py
│       │   ├── main.py
│       │   ├── nl_workflow.py
│       │   ├── nl_workflow_routes.py
│       │   ├── workflow_audit.py
│       │   ├── workflow_definitions.py
│       │   ├── workflow_runtime.py
│       │   └── workflow_storage.py
│       ├── storage
│       │   └── workflows.db
│       ├── tests
│       │   ├── README.md
│       │   ├── test_storage_policy.py
│       │   └── test_workflow_storage_concurrency.py
│       ├── workflow_registry.py
│       └── workflows
│           ├── README.md
│           ├── definitions
│           │   ├── change-request.workflow.yaml
│           │   ├── deployment-rollback.workflow.yaml
│           │   ├── intake-triage.workflow.yaml
│           │   ├── project-initiation.workflow.yaml
│           │   ├── publish-charter.workflow.yaml
│           │   ├── quality-audit.workflow.yaml
│           │   └── risk-mitigation.workflow.yaml
│           └── schema
│               └── workflow.schema.json
├── config
│   ├── abac
│   │   ├── policies.yaml
│   │   └── rules.yaml
│   └── rbac
│       ├── field-level.yaml
│       ├── permissions.yaml
│       └── roles.yaml
├── connectors
│   ├── README.md
│   ├── __init__.py
│   ├── adp
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── adp_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── archer
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── archer_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── asana
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── asana_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── asana_mcp
│   │   └── manifest.yaml
│   ├── azure_communication_services
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── azure_communication_services_connector.py
│   │   │   ├── main.py
│   │   │   ├── router.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── azure_devops
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   ├── project.yaml
│   │   │   └── work-item.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── azure_devops_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── clarity
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── clarity_connector.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   ├── router.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_clarity_connector.py
│   │       ├── test_clarity_mcp.py
│   │       ├── test_clarity_runtime.py
│   │       ├── test_contract.py
│   │       ├── test_mappers.py
│   │       └── test_outbound_sync.py
│   ├── clarity_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── confluence
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── confluence_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── conftest.py
│   ├── google_calendar
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── google_calendar_connector.py
│   │   │   ├── main.py
│   │   │   ├── router.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── google_drive
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── google_drive_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── integration
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── framework.py
│   │   └── mcp_connectors.py
│   ├── iot
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── sensor-data.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── iot_connector.py
│   │   │   └── main.py
│   │   └── tests
│   │       ├── test_contract.py
│   │       └── test_iot_connector.py
│   ├── jira
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   ├── project.yaml
│   │   │   └── work-item.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── jira_connector.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── conftest.py
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       ├── test_jira_connector.py
│   │       └── test_jira_mcp.py
│   ├── jira_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── work-item.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── logicgate
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── logicgate_connector.py
│   │   │   ├── main.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── m365
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── resource.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── m365_connector.py
│   │   │   └── main.py
│   │   ├── tests
│   │   │   └── test_contract.py
│   │   └── tool_map.yaml
│   ├── mcp_client
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── client.py
│   │   ├── errors.py
│   │   └── models.py
│   ├── mock
│   │   ├── __init__.py
│   │   ├── azure_devops
│   │   │   └── manifest.yaml
│   │   ├── clarity
│   │   │   └── manifest.yaml
│   │   ├── jira
│   │   │   └── manifest.yaml
│   │   ├── mock_connectors.py
│   │   ├── planview
│   │   │   └── manifest.yaml
│   │   ├── sap
│   │   │   └── manifest.yaml
│   │   ├── servicenow
│   │   │   └── manifest.yaml
│   │   ├── teams
│   │   │   └── manifest.yaml
│   │   └── workday
│   │       └── manifest.yaml
│   ├── monday
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── monday_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── ms_project_server
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── ms_project_server_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── netsuite
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── netsuite_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── notification_hubs
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── notification_hubs_connector.py
│   │   │   ├── router.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── oracle
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── oracle_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── outlook
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── outlook_connector.py
│   │   │   ├── router.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── planview
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   ├── planview_connector.py
│   │   │   ├── router.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── conftest.py
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       ├── test_mappers.py
│   │       ├── test_outbound_sync.py
│   │       ├── test_planview_connector.py
│   │       ├── test_planview_mcp.py
│   │       └── test_planview_runtime.py
│   ├── planview_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── registry
│   │   ├── README.md
│   │   ├── connectors.json
│   │   ├── generate.py
│   │   ├── schemas
│   │   │   ├── auth-config.schema.json
│   │   │   ├── capabilities.schema.json
│   │   │   ├── connector-manifest.schema.json
│   │   │   └── connector-mapping.schema.json
│   │   └── signing
│   │       ├── README.md
│   │       ├── public-keys
│   │       │   └── README.md
│   │       └── signing-policy.md
│   ├── regulatory_compliance
│   │   ├── Dockerfile
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── audit_trail.yaml
│   │   │   ├── compliance_event.yaml
│   │   │   └── finding.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── regulatory_compliance_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── conftest.py
│   │       └── test_regulatory_compliance_connector.py
│   ├── salesforce
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   └── router.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       └── test_router.py
│   ├── sap
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   ├── router.py
│   │   │   ├── sap_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       ├── test_mappers.py
│   │       ├── test_outbound_sync.py
│   │       └── test_sap_mcp.py
│   ├── sap_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── purchase-order.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── sap_successfactors
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── sap_successfactors_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── sdk
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── connector_maturity_inventory.py
│   │   ├── connector_migration_tracker.md
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── base_connector.py
│   │   │   ├── classification.py
│   │   │   ├── clients
│   │   │   │   ├── erp_client.py
│   │   │   │   ├── hris_client.py
│   │   │   │   └── ppm_client.py
│   │   │   ├── connector_registry.py
│   │   │   ├── connector_secrets.py
│   │   │   ├── data_service_client.py
│   │   │   ├── http_client.py
│   │   │   ├── iot_connector.py
│   │   │   ├── mcp_client.py
│   │   │   ├── operation_router.py
│   │   │   ├── project_connector_store.py
│   │   │   ├── quality.py
│   │   │   ├── regulatory_compliance_connector.py
│   │   │   ├── rest_connector.py
│   │   │   ├── runtime.py
│   │   │   ├── sync_controls.py
│   │   │   ├── sync_router.py
│   │   │   ├── telemetry.py
│   │   │   └── transformations.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── connector_contract_fixture.json
│   │       ├── test_auth.py
│   │       ├── test_connector_contract_harness.py
│   │       ├── test_connector_runtime.py
│   │       ├── test_http_client.py
│   │       ├── test_mcp_client.py
│   │       ├── test_mcp_project_config.py
│   │       └── test_rest_connector_docs.py
│   ├── servicenow
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── router.py
│   │   │   ├── servicenow_grc_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       └── test_router.py
│   ├── sharepoint
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── sharepoint_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── slack
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   ├── project.yaml
│   │   │   └── resource.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   ├── router.py
│   │   │   ├── slack_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── conftest.py
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       └── test_slack_mcp.py
│   ├── slack_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── resource.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── smartsheet
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── router.py
│   │   │   ├── smartsheet_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── teams
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   ├── router.py
│   │   │   ├── teams_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       └── test_teams_mcp.py
│   ├── teams_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── resource.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   ├── twilio
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   └── project.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── router.py
│   │   │   ├── twilio_connector.py
│   │   │   └── webhooks.py
│   │   └── tests
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       └── test_contract.py
│   ├── workday
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── README.md
│   │   │   ├── project.yaml
│   │   │   └── resource.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── mappers.py
│   │   │   ├── router.py
│   │   │   ├── webhooks.py
│   │   │   └── workday_connector.py
│   │   └── tests
│   │       ├── README.md
│   │       ├── fixtures
│   │       │   └── projects.json
│   │       ├── test_contract.py
│   │       ├── test_router.py
│   │       └── test_workday_mcp.py
│   ├── workday_mcp
│   │   ├── manifest.yaml
│   │   ├── mappings
│   │   │   ├── project.yaml
│   │   │   └── resource.yaml
│   │   ├── src
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_contract.py
│   └── zoom
│       ├── README.md
│       ├── manifest.yaml
│       ├── mappings
│       │   └── project.yaml
│       ├── src
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── webhooks.py
│       │   └── zoom_connector.py
│       └── tests
│           └── test_contract.py
├── constraints
│   └── py313.txt
├── data
│   ├── README.md
│   ├── __init__.py
│   ├── alerts.json
│   ├── analytics_alerts.json
│   ├── analytics_events.json
│   ├── analytics_kpi_history.json
│   ├── analytics_lineage.json
│   ├── analytics_outputs.json
│   ├── approval_notification_store.json
│   ├── approval_store.json
│   ├── audit
│   │   └── audit_logs.db
│   ├── business_case_store.json
│   ├── change_requests.json
│   ├── cmdb.json
│   ├── compliance_evidence.json
│   ├── demand_intake_store.json
│   ├── demo
│   │   ├── approvals.json
│   │   ├── budgets.json
│   │   ├── contracts.json
│   │   ├── demo_run_log.json
│   │   ├── epics.json
│   │   ├── issues.json
│   │   ├── notifications.json
│   │   ├── policies.json
│   │   ├── portfolios.json
│   │   ├── programs.json
│   │   ├── projects.json
│   │   ├── resources.json
│   │   ├── risks.json
│   │   ├── sprints.json
│   │   ├── tasks.json
│   │   └── vendors.json
│   ├── deployment_plans.json
│   ├── financial_actuals.json
│   ├── financial_budgets.json
│   ├── financial_forecasts.json
│   ├── fixtures
│   │   ├── exchange_rates.json
│   │   └── tax_rates.json
│   ├── health_snapshots.json
│   ├── improvement_backlog.json
│   ├── improvement_history.json
│   ├── incidents.json
│   ├── knowledge_documents.json
│   ├── knowledge_management.db
│   ├── lineage
│   │   ├── README.md
│   │   ├── example-lineage.json
│   │   └── sync_lineage.json
│   ├── master_records.json
│   ├── migrations
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── env.py
│   │   ├── models.py
│   │   ├── validate_registry_consistency.py
│   │   └── versions
│   │       ├── 0001_create_core_tables.py
│   │       ├── 0002_create_orchestration_states.py
│   │       ├── 0003_create_missing_tables.py
│   │       ├── 0004_add_enum_constraints.py
│   │       ├── 0005_create_workflow_engine_tables.py
│   │       ├── 0006_add_integration_config_tables.py
│   │       ├── 0007_add_idempotency_key_to_workflow_instances.py
│   │       ├── 0008_add_entities_schema_version_index.py
│   │       ├── 0009_create_schema_registry_tables.py
│   │       ├── 0010_add_structured_skills_taxonomy.py
│   │       └── 0011_add_methodology_definitions.py
│   ├── portfolio_strategy_store.json
│   ├── process_conformance.json
│   ├── process_event_logs.json
│   ├── process_models.json
│   ├── process_recommendations.json
│   ├── program_dependency_store.json
│   ├── program_roadmap_store.json
│   ├── program_store.json
│   ├── project_charters.json
│   ├── project_health_history.json
│   ├── project_lifecycle.json
│   ├── project_schedules.json
│   ├── project_wbs.json
│   ├── quality
│   │   ├── README.md
│   │   └── rules.yaml
│   ├── quality_audits.json
│   ├── quality_coverage_trends.json
│   ├── quality_defects.json
│   ├── quality_plans.json
│   ├── quality_requirement_links.json
│   ├── quality_test_cases.json
│   ├── release_calendar.json
│   ├── resource_allocations.json
│   ├── resource_calendars.json
│   ├── resource_pool.json
│   ├── risk_register.json
│   ├── rollback_scripts
│   │   └── rollback_DEPLOY-TEST.sh
│   ├── schedule_baselines.json
│   ├── schema_registry.json
│   ├── schemas
│   │   ├── README.md
│   │   ├── agent-manifest.schema.json
│   │   ├── agent-run.schema.json
│   │   ├── agent_config.schema.json
│   │   ├── audit-event.schema.json
│   │   ├── budget.schema.json
│   │   ├── demand.schema.json
│   │   ├── document.schema.json
│   │   ├── examples
│   │   │   ├── agent_config.json
│   │   │   ├── audit-event.json
│   │   │   ├── budget.json
│   │   │   ├── demand.json
│   │   │   ├── document.json
│   │   │   ├── issue.json
│   │   │   ├── portfolio.json
│   │   │   ├── program.json
│   │   │   ├── project.json
│   │   │   ├── resource.json
│   │   │   ├── risk.json
│   │   │   ├── roi.json
│   │   │   ├── vendor.json
│   │   │   └── work-item.json
│   │   ├── issue.schema.json
│   │   ├── methodology.schema.json
│   │   ├── portfolio.schema.json
│   │   ├── program.schema.json
│   │   ├── project.schema.json
│   │   ├── resource.schema.json
│   │   ├── risk.schema.json
│   │   ├── roi.schema.json
│   │   ├── scenario.schema.json
│   │   ├── vendor.schema.json
│   │   └── work-item.schema.json
│   ├── scope_baselines.db
│   ├── scope_baselines.json
│   ├── seed
│   │   └── manifest.csv
│   ├── stakeholder_comms.db
│   ├── stakeholders.json
│   ├── sync_audit_events.json
│   ├── sync_events.json
│   ├── sync_retry_queue.json
│   ├── sync_state.json
│   ├── vendor_contracts.json
│   ├── vendor_invoices.json
│   ├── vendor_performance.json
│   ├── vendor_procurement_events.json
│   ├── vendors.json
│   ├── workflow_events.json
│   ├── workflow_instances.json
│   ├── workflow_subscriptions.json
│   ├── workflow_tasks.json
│   └── workflows.json
├── docs
│   ├── CHANGELOG.md
│   ├── README.md
│   ├── REPO_STRUCTURE.md
│   ├── UI.md
│   ├── agents.md
│   ├── api
│   │   ├── README.md
│   │   ├── analytics-openapi.yaml
│   │   ├── connector-hub-openapi.yaml
│   │   ├── document-openapi.yaml
│   │   ├── graphql-schema.graphql
│   │   ├── openapi.yaml
│   │   └── orchestration-openapi.yaml
│   ├── architecture
│   │   ├── README.md
│   │   ├── adr
│   │   │   ├── 0000-adr-template.md
│   │   │   ├── 0001-record-architecture.md
│   │   │   ├── 0002-llm-provider-abstraction.md
│   │   │   ├── 0003-eventing-and-message-bus.md
│   │   │   ├── 0004-workflow-service-selection.md
│   │   │   ├── 0005-rbac-abac-field-level-security.md
│   │   │   ├── 0006-data-lineage-and-audit.md
│   │   │   ├── 0007-connector-certification.md
│   │   │   ├── 0008-prompt-management-and-versioning.md
│   │   │   ├── 0009-multi-tenancy-strategy.md
│   │   │   └── 0010-secrets-management.md
│   │   ├── diagrams
│   │   │   ├── c4-component.puml
│   │   │   ├── c4-container.puml
│   │   │   ├── c4-context.puml
│   │   │   ├── data-lineage.puml
│   │   │   ├── deployment-overview.puml
│   │   │   ├── seq-connector-sync.puml
│   │   │   ├── seq-intent-routing.puml
│   │   │   ├── seq-stage-gate-enforcement.puml
│   │   │   ├── service-topology.puml
│   │   │   └── threat-model-flow.puml
│   │   ├── grafana
│   │   │   ├── cost_dashboard.json
│   │   │   └── multi_agent_tracing.json
│   │   └── images
│   │       ├── grafana-ppm-platform.svg
│   │       └── grafana-ppm-slo.svg
│   ├── assets
│   │   └── ui
│   │       └── screenshots
│   │           └── README.md
│   ├── change-management.md
│   ├── compliance.md
│   ├── connectors
│   │   ├── README.md
│   │   └── generated
│   │       ├── capability-matrix.md
│   │       └── maturity-inventory.json
│   ├── data.md
│   ├── demo-environment.md
│   ├── dependency-management.md
│   ├── design-system.md
│   ├── dr-runbook.md
│   ├── frontend-spa-migration.md
│   ├── generated
│   │   └── services
│   │       ├── README.md
│   │       ├── agent-config.md
│   │       ├── agent-runtime.md
│   │       ├── audit-log.md
│   │       ├── auth-service.md
│   │       ├── data-lineage-service.md
│   │       ├── data-service.md
│   │       ├── data-sync-service.md
│   │       ├── identity-access.md
│   │       ├── memory-service.md
│   │       ├── notification-service.md
│   │       ├── policy-engine.md
│   │       ├── realtime-coedit-service.md
│   │       └── telemetry-service.md
│   ├── merge-conflict-troubleshooting.md
│   ├── methodology
│   │   ├── README.md
│   │   ├── adaptive
│   │   │   ├── README.md
│   │   │   ├── gates.yaml
│   │   │   └── map.yaml
│   │   ├── customisation-guide.md
│   │   ├── hybrid
│   │   │   ├── README.md
│   │   │   ├── gates.yaml
│   │   │   └── map.yaml
│   │   └── predictive
│   │       ├── README.md
│   │       ├── gates.yaml
│   │       └── map.yaml
│   ├── onboarding
│   │   └── developer-onboarding.md
│   ├── outbound_dependency_inventory.md
│   ├── platform-commercials.md
│   ├── platform-description.md
│   ├── platform-userguide.md
│   ├── production-readiness
│   │   ├── README.md
│   │   └── maturity-scorecards
│   │       ├── README.md
│   │       └── latest.md
│   ├── react-native-typescript-alignment.md
│   ├── root-file-policy.md
│   ├── runbooks
│   │   ├── backup-recovery.md
│   │   ├── credential-acquisition.md
│   │   ├── deployment.md
│   │   ├── disaster-recovery.md
│   │   ├── monitoring-dashboards.md
│   │   ├── schema-promotion-rollback.md
│   │   ├── secret-init.md
│   │   ├── secret-rotation.md
│   │   └── troubleshooting.md
│   ├── runbooks.md
│   ├── schema-compatibility-matrix.md
│   ├── solution-index.md
│   ├── templates
│   │   ├── CHANGELOG.md
│   │   ├── Executive-Report-Templates.md
│   │   ├── README.md
│   │   ├── advanced-business-case-template.md
│   │   ├── agile-ceremonies-templates.md
│   │   ├── agile-release-plan-template.md
│   │   ├── agile-risk-board-template.md
│   │   ├── agile-scrum-framework.md
│   │   ├── agile-stakeholder-map-template.md
│   │   ├── agile-team-charter-template.md
│   │   ├── ai-implementation-status.md
│   │   ├── api_documentation_template.md
│   │   ├── architecture_decision_record.md
│   │   ├── art_coordination_template.md
│   │   ├── backlog-management-template.md
│   │   ├── backlog-refinement-template.md
│   │   ├── batch_record_template.md
│   │   ├── budget-dashboard-template.md
│   │   ├── budget-template.md
│   │   ├── business-case.md
│   │   ├── business-continuity-disaster-recovery-plan.md
│   │   ├── business_case_template.md
│   │   ├── business_requirements_document_template.md
│   │   ├── capacity-planning-worksheet.md
│   │   ├── change-management-plan.md
│   │   ├── change-request.md
│   │   ├── change_management_plan_template.md
│   │   ├── change_request_template.md
│   │   ├── ci-cd-pipeline-definition.md
│   │   ├── cicd_pipeline_planning_template.md
│   │   ├── cleaning_validation_protocol_template.md
│   │   ├── clinical-trial-project-charter.md
│   │   ├── clinical_trial_protocol_template.md
│   │   ├── closure-checklist.md
│   │   ├── communication-plan.md
│   │   ├── compliance-management-template.md
│   │   ├── compliance-risk-assessment.md
│   │   ├── compliance_risk_assessment_template.md
│   │   ├── components
│   │   │   ├── assumptions.yaml
│   │   │   ├── benefits.yaml
│   │   │   ├── controls.yaml
│   │   │   ├── core-communication-plan--data-table.yaml
│   │   │   ├── core-deployment-checklist--deployment.yaml
│   │   │   ├── core-deployment-checklist--post-deployment.yaml
│   │   │   ├── core-deployment-checklist--pre-deployment.yaml
│   │   │   ├── core-executive-dashboard--budget-performance.yaml
│   │   │   ├── core-executive-dashboard--decisions-required.yaml
│   │   │   ├── core-executive-dashboard--portfolio-health.yaml
│   │   │   ├── core-executive-dashboard--schedule-performance.yaml
│   │   │   ├── core-product-backlog--data-table.yaml
│   │   │   ├── core-project-charter--budget-summary.yaml
│   │   │   ├── core-project-charter--governance.yaml
│   │   │   ├── core-project-charter--objectives.yaml
│   │   │   ├── core-project-charter--problem-statement.yaml
│   │   │   ├── core-project-charter--scope.yaml
│   │   │   ├── core-project-charter--success-criteria.yaml
│   │   │   ├── core-project-management-plan--cost-baseline.yaml
│   │   │   ├── core-project-management-plan--management-approach.yaml
│   │   │   ├── core-project-management-plan--project-overview.yaml
│   │   │   ├── core-project-management-plan--schedule-baseline.yaml
│   │   │   ├── core-project-management-plan--scope-baseline.yaml
│   │   │   ├── core-project-management-plan--stakeholder-engagement.yaml
│   │   │   ├── core-requirements--acceptance-criteria.yaml
│   │   │   ├── core-requirements--business-requirements.yaml
│   │   │   ├── core-requirements--constraints.yaml
│   │   │   ├── core-requirements--functional-requirements.yaml
│   │   │   ├── core-requirements--non-functional-requirements.yaml
│   │   │   ├── core-requirements--traceability.yaml
│   │   │   ├── core-risk-register--data-table.yaml
│   │   │   ├── core-sprint-planning--candidate-work.yaml
│   │   │   ├── core-sprint-planning--capacity.yaml
│   │   │   ├── core-sprint-planning--commitment.yaml
│   │   │   ├── core-sprint-planning--dependencies.yaml
│   │   │   ├── core-sprint-planning--sprint-goal.yaml
│   │   │   ├── core-sprint-retrospective--experiments.yaml
│   │   │   ├── core-sprint-retrospective--owners-and-dates.yaml
│   │   │   ├── core-sprint-retrospective--root-causes.yaml
│   │   │   ├── core-sprint-retrospective--what-did-not-go-well.yaml
│   │   │   ├── core-sprint-retrospective--what-went-well.yaml
│   │   │   ├── core-sprint-review--backlog-adjustments.yaml
│   │   │   ├── core-sprint-review--completed-increment.yaml
│   │   │   ├── core-sprint-review--rejected-or-carried-over-items.yaml
│   │   │   ├── core-sprint-review--sprint-goal-outcome.yaml
│   │   │   ├── core-sprint-review--stakeholder-feedback.yaml
│   │   │   ├── core-status-report--budget-status.yaml
│   │   │   ├── core-status-report--decisions-needed.yaml
│   │   │   ├── core-status-report--next-period-plan.yaml
│   │   │   ├── core-status-report--overall-health-rag.yaml
│   │   │   ├── core-status-report--progress-vs-plan.yaml
│   │   │   ├── core-status-report--reporting-period.yaml
│   │   │   ├── core-status-report--summary.yaml
│   │   │   ├── milestones.yaml
│   │   │   └── risks.yaml
│   │   ├── computer_system_validation_protocol_template.md
│   │   ├── configuration-management-plan.md
│   │   ├── construction-pm-templates.md
│   │   ├── construction-project-charter.md
│   │   ├── construction-risk-register.md
│   │   ├── construction-wbs.md
│   │   ├── core
│   │   │   ├── communication-plan
│   │   │   │   └── manifest.yaml
│   │   │   ├── deployment-checklist
│   │   │   │   └── manifest.yaml
│   │   │   ├── executive-dashboard
│   │   │   │   └── manifest.yaml
│   │   │   ├── product-backlog
│   │   │   │   └── manifest.yaml
│   │   │   ├── project-charter
│   │   │   │   └── manifest.yaml
│   │   │   ├── project-management-plan
│   │   │   │   └── manifest.yaml
│   │   │   ├── requirements
│   │   │   │   └── manifest.yaml
│   │   │   ├── risk-register
│   │   │   │   └── manifest.yaml
│   │   │   ├── sprint-planning
│   │   │   │   └── manifest.yaml
│   │   │   ├── sprint-retrospective
│   │   │   │   └── manifest.yaml
│   │   │   ├── sprint-review
│   │   │   │   └── manifest.yaml
│   │   │   └── status-report
│   │   │       └── manifest.yaml
│   │   ├── cross_team_coordination_template.md
│   │   ├── current-state-analysis-template.md
│   │   ├── cybersecurity-training-plan.md
│   │   ├── cybersecurity_assessment_template.md
│   │   ├── daily-standup-template.md
│   │   ├── data-quality-framework.md
│   │   ├── data_center_design_template.md
│   │   ├── decision-authority.md
│   │   ├── decision-framework.md
│   │   ├── decision-log.md
│   │   ├── deployment-checklist.md
│   │   ├── devsecops_template.md
│   │   ├── digital-kpi-dashboard.md
│   │   ├── digital-maturity-assessment.md
│   │   ├── digital_transformation_strategy_template.md
│   │   ├── disaster_recovery_template.md
│   │   ├── enterprise-risk-assessment-template.md
│   │   ├── enterprise-stakeholder-analysis-template.md
│   │   ├── equipment_qualification_protocol_template.md
│   │   ├── escalation-matrix.md
│   │   ├── evm-dashboard-template.md
│   │   ├── executive-communication-automation.md
│   │   ├── executive-dashboard-slides.md
│   │   ├── executive-dashboard-workbook.md
│   │   ├── executive-dashboard.md
│   │   ├── executive-status-report.md
│   │   ├── executive-summary-template.md
│   │   ├── extensions
│   │   │   ├── agile
│   │   │   │   ├── product-backlog.patch.yaml
│   │   │   │   ├── project-charter.patch.yaml
│   │   │   │   ├── risk-register.patch.yaml
│   │   │   │   ├── sprint-planning.patch.yaml
│   │   │   │   ├── sprint-retrospective.patch.yaml
│   │   │   │   ├── sprint-review.patch.yaml
│   │   │   │   └── status-report.patch.yaml
│   │   │   ├── compliance
│   │   │   │   └── privacy
│   │   │   │       └── project-charter.patch.yaml
│   │   │   ├── devops
│   │   │   │   └── deployment-checklist.patch.yaml
│   │   │   ├── hybrid
│   │   │   │   ├── project-charter.patch.yaml
│   │   │   │   ├── project-management-plan.patch.yaml
│   │   │   │   ├── risk-register.patch.yaml
│   │   │   │   └── status-report.patch.yaml
│   │   │   ├── safe
│   │   │   │   ├── executive-dashboard.patch.yaml
│   │   │   │   ├── product-backlog.patch.yaml
│   │   │   │   ├── risk-register.patch.yaml
│   │   │   │   ├── sprint-planning.patch.yaml
│   │   │   │   └── status-report.patch.yaml
│   │   │   └── waterfall
│   │   │       ├── project-charter.patch.yaml
│   │   │       ├── project-management-plan.patch.yaml
│   │   │       ├── requirements.patch.yaml
│   │   │       └── status-report.patch.yaml
│   │   ├── final-report.md
│   │   ├── financial-forecasting-models.md
│   │   ├── financial-services-pm-templates.md
│   │   ├── financial_services_project_charter.md
│   │   ├── future-state-blueprint-template.md
│   │   ├── gap-analysis-matrix-template.md
│   │   ├── github-projects-integration-toolkit.md
│   │   ├── governance-assessment-template.md
│   │   ├── governance-charter.md
│   │   ├── governance-framework.md
│   │   ├── governance-roles.md
│   │   ├── guides
│   │   │   ├── agent-generation-patterns.md
│   │   │   └── tailoring-playbook.md
│   │   ├── gxp-compliance-checklist.md
│   │   ├── gxp_training_plan_template.md
│   │   ├── handover-template.md
│   │   ├── health-pharma-pm-templates.md
│   │   ├── health_authority_communication_plan_template.md
│   │   ├── healthcare-risk-register.md
│   │   ├── hybrid-infrastructure-template.md
│   │   ├── hybrid-pm-templates--tools.md
│   │   ├── hybrid-project-management-plan-template.md
│   │   ├── hybrid_project_charter_template.md
│   │   ├── hybrid_quality_management_template.md
│   │   ├── hybrid_release_planning_template.md
│   │   ├── hybrid_team_management_template.md
│   │   ├── incident-response-plan.md
│   │   ├── incident_response_template.md
│   │   ├── index.json
│   │   ├── infrastructure-change-management-protocol.md
│   │   ├── infrastructure-requirements-template.md
│   │   ├── infrastructure_as_code_template.md
│   │   ├── infrastructure_assessment_template.md
│   │   ├── installation_qualification_protocol_template.md
│   │   ├── integrated_change_strategy_template.md
│   │   ├── integration-toolkits.md
│   │   ├── issue-alignment-summary.md
│   │   ├── issue-log.md
│   │   ├── issue_log_template.md
│   │   ├── it-pm-templates.md
│   │   ├── it-project-charter.md
│   │   ├── it-risk-register.md
│   │   ├── jira-integration-toolkit.md
│   │   ├── less_retrospective_template.md
│   │   ├── lessons-learned.md
│   │   ├── manufacturing_batch_record_template.md
│   │   ├── mappings
│   │   │   └── template-field-map.json
│   │   ├── meeting-templates.md
│   │   ├── methodology-comparison.md
│   │   ├── methodology-selector.md
│   │   ├── metrics_dashboard_template.md
│   │   ├── migration
│   │   │   ├── consolidation-map.md
│   │   │   ├── dependency-map.json
│   │   │   ├── legacy-to-canonical.csv
│   │   │   └── migration-status.csv
│   │   ├── migration_plan_template.md
│   │   ├── milestone-review.md
│   │   ├── monitoring_alerting_template.md
│   │   ├── ms-project-integration-toolkit.md
│   │   ├── okr-template.md
│   │   ├── operational_qualification_protocol_template.md
│   │   ├── organizational_change_management_framework.md
│   │   ├── overall_product_backlog_template.md
│   │   ├── performance-dashboard.md
│   │   ├── performance_qualification_protocol_template.md
│   │   ├── pharmaceutical_qbd_template.md
│   │   ├── pi_planning_template.md
│   │   ├── pm-utilities.md
│   │   ├── portfolio-financial-aggregation.md
│   │   ├── portfolio_kanban_template.md
│   │   ├── prioritization-framework-guide.md
│   │   ├── problem_management_process_template.md
│   │   ├── process-digitization-workflow.md
│   │   ├── process-maturity-assessment-template.md
│   │   ├── process_control_template.md
│   │   ├── process_validation_master_plan_template.md
│   │   ├── process_validation_protocol_template.md
│   │   ├── product-metrics-dashboard.md
│   │   ├── product-owner-templates.md
│   │   ├── product-strategy-canvas.md
│   │   ├── product-vision-template.md
│   │   ├── product_backlog_example.md
│   │   ├── product_backlog_template.md
│   │   ├── professional-standards.md
│   │   ├── program-manager-pm-templates.md
│   │   ├── program_charter_template.md
│   │   ├── program_management_plan_template.md
│   │   ├── progressive-complexity.md
│   │   ├── progressive_acceptance_plan_template.md
│   │   ├── project-charter-example.md
│   │   ├── project-closure-phase.md
│   │   ├── project-dashboard-template.md
│   │   ├── project-execution-phase.md
│   │   ├── project-health-assessment-template.md
│   │   ├── project-initiation-phase.md
│   │   ├── project-intelligence-cli-gateway.md
│   │   ├── project-intelligence-cli-implementation-report.md
│   │   ├── project-management-plan-example.md
│   │   ├── project-monitoring-control-phase.md
│   │   ├── project-planning-phase.md
│   │   ├── project-schedule.md
│   │   ├── project_closure_report_template.md
│   │   ├── project_execution_status_report_template.md
│   │   ├── project_management_plan_template.md
│   │   ├── project_performance_monitoring_template.md
│   │   ├── project_roadmap_template.md
│   │   ├── project_schedule_template.md
│   │   ├── purchase_order_template.md
│   │   ├── quality-checklist.md
│   │   ├── quality-prediction.md
│   │   ├── quality-test-plan-template.md
│   │   ├── quality_management_review_template.md
│   │   ├── raid_log_template.md
│   │   ├── real-time-budget-variance-analysis.md
│   │   ├── real-time-data-sync.md
│   │   ├── regulatory_inspection_readiness_plan_template.md
│   │   ├── regulatory_strategy_plan_template.md
│   │   ├── release_management_template.md
│   │   ├── remediation-action-plan-template.md
│   │   ├── requirements_traceability_matrix_template.md
│   │   ├── resource-management-assessment-template.md
│   │   ├── resource-management-plan-template.md
│   │   ├── resource-optimization.md
│   │   ├── resource-planning.md
│   │   ├── risk-assessment-framework.md
│   │   ├── risk-management-assessment-template.md
│   │   ├── risk-management-plan-template.md
│   │   ├── risk-prediction.md
│   │   ├── risk-register.md
│   │   ├── risk_assessment_template.md
│   │   ├── roadmap-product-backlog.md
│   │   ├── roi-sample-data.csv
│   │   ├── roi-setup-guide.md
│   │   ├── roi-tracking-automation.md
│   │   ├── roi_tracking_template.md
│   │   ├── safe_art_coordination_template.md
│   │   ├── safe_metrics_dashboard_template.md
│   │   ├── safe_metrics_reporting_template.md
│   │   ├── safe_portfolio_kanban_template.md
│   │   ├── safe_program_increment_planning_template.md
│   │   ├── schedule-intelligence.md
│   │   ├── schemas
│   │   │   ├── README.md
│   │   │   └── examples
│   │   │       ├── core-project-charter.example.yaml
│   │   │       └── extension-agile-status-report.example.yaml
│   │   ├── scope-statement.md
│   │   ├── security-awareness-program.md
│   │   ├── security-change-management-protocol.md
│   │   ├── security-controls-matrix.md
│   │   ├── security-implementation-roadmap.md
│   │   ├── setup.md
│   │   ├── skills-matrix-template.md
│   │   ├── software-development-pm-templates.md
│   │   ├── software-project-charter.md
│   │   ├── software-requirements-specification-template.md
│   │   ├── software-risk-register.md
│   │   ├── software-test-plan.md
│   │   ├── sprint-planning-template.md
│   │   ├── sprint-retrospective-template.md
│   │   ├── sprint-review-template.md
│   │   ├── sprint_planning_example.md
│   │   ├── sprint_retrospective_example.md
│   │   ├── sprint_review_example.md
│   │   ├── stakeholder-collaboration-framework.md
│   │   ├── stakeholder-engagement-assessment-template.md
│   │   ├── stakeholder-register.md
│   │   ├── stakeholder-update.md
│   │   ├── stakeholder_communication_planning.md
│   │   ├── standards
│   │   │   ├── index-governance.md
│   │   │   ├── modularization.md
│   │   │   ├── placeholders.md
│   │   │   ├── tailoring-guidance.md
│   │   │   ├── template-naming-rules.md
│   │   │   └── template-taxonomy.md
│   │   ├── status-report.md
│   │   ├── story-writing-checklist.md
│   │   ├── system-security-plan.md
│   │   ├── team-assignments.md
│   │   ├── team-charter-template.md
│   │   ├── team-charter.md
│   │   ├── team-dashboard.md
│   │   ├── team-performance-assessment-template.md
│   │   ├── technical-debt-log.md
│   │   ├── technical-design-document-template.md
│   │   ├── technology-adoption-roadmap.md
│   │   ├── template-index.md
│   │   ├── template-selector.md
│   │   ├── test-plan-template.md
│   │   ├── timesheet-tracking-template.md
│   │   ├── traditional-project-charter-template.md
│   │   ├── traditional-project-management-plan-template.md
│   │   ├── uat-plan-template.md
│   │   ├── uat-strategy-template.md
│   │   ├── user-story-mapping-template.md
│   │   ├── user-story-template.md
│   │   ├── user_story_template.md
│   │   ├── validation-master-plan-template.md
│   │   ├── validation_master_plan.md
│   │   ├── vulnerability-management-plan.md
│   │   ├── waterfall-project-assessment-template.md
│   │   ├── work-breakdown-structure-template.md
│   │   └── work-breakdown-structure.md
│   ├── testing
│   │   └── README.md
│   └── versioning.md
├── examples
│   ├── README.md
│   ├── abac-evaluation.json
│   ├── connector-configs
│   │   ├── README.md
│   │   └── mcp-project-config.json
│   ├── demo-scenarios
│   │   ├── README.md
│   │   ├── approvals.json
│   │   ├── assistant-responses.json
│   │   ├── full-platform-expected-output.json
│   │   ├── full-platform-llm-response.json
│   │   ├── full-platform-request.json
│   │   ├── full-platform-workflow.json
│   │   ├── global-search.json
│   │   ├── lifecycle-metrics.json
│   │   ├── portfolio-health.json
│   │   ├── quickstart-expected-output.json
│   │   ├── quickstart-llm-response.json
│   │   ├── quickstart-request.json
│   │   ├── quickstart-workflow.json
│   │   ├── schedule.json
│   │   ├── wbs.json
│   │   └── workflow-monitoring.json
│   ├── integration_demo.py
│   ├── mcp_cross_system_demo.py
│   ├── methodology-maps
│   │   └── README.md
│   ├── portfolio-intake-request.json
│   ├── schema
│   │   └── portfolio-intake.schema.json
│   └── workflows
│       ├── README.md
│       ├── mcp-cross-system.workflow.yaml
│       └── portfolio-intake.workflow.yaml
├── integrations
│   ├── __init__.py
│   └── services
│       ├── __init__.py
│       └── integration
│           ├── README.md
│           ├── __init__.py
│           ├── ai_models.py
│           ├── analytics.py
│           ├── databricks.py
│           ├── event_bus.py
│           ├── external_sync.py
│           ├── ml.py
│           └── persistence.py
├── mkdocs.yml
├── ops
│   ├── config
│   │   ├── .env.demo
│   │   ├── .env.example
│   │   ├── README.md
│   │   ├── agents
│   │   │   ├── README.md
│   │   │   ├── approval-workflow-agent
│   │   │   │   ├── durable_workflows.yaml
│   │   │   │   └── workflow_templates.yaml
│   │   │   ├── approval_policies.yaml
│   │   │   ├── approval_workflow.yaml
│   │   │   ├── business-case-settings.yaml
│   │   │   ├── data-synchronisation-agent
│   │   │   │   ├── mapping_rules.yaml
│   │   │   │   ├── pipelines.yaml
│   │   │   │   ├── quality_thresholds.yaml
│   │   │   │   ├── schema_registry.yaml
│   │   │   │   └── validation_rules.yaml
│   │   │   ├── demo-participants.yaml
│   │   │   ├── intent-router.yaml
│   │   │   ├── intent-routing.yaml
│   │   │   ├── knowledge_agent.yaml
│   │   │   ├── orchestration.yaml
│   │   │   ├── portfolio.yaml
│   │   │   ├── risk_adjustments.yaml
│   │   │   └── schema
│   │   │       └── intent-routing.schema.json
│   │   ├── alembic.ini
│   │   ├── approval_policies.json
│   │   ├── common.yaml
│   │   ├── connector_maturity_policy.yaml
│   │   ├── connectors
│   │   │   ├── integrations.yaml
│   │   │   └── mock
│   │   │       ├── README.md
│   │   │       ├── azure_devops.yaml
│   │   │       ├── clarity.yaml
│   │   │       ├── jira.yaml
│   │   │       ├── planview.yaml
│   │   │       ├── sap.yaml
│   │   │       ├── servicenow.yaml
│   │   │       ├── teams.yaml
│   │   │       └── workday.yaml
│   │   ├── data-classification
│   │   │   └── levels.yaml
│   │   ├── demo-workflows
│   │   │   ├── approval-gating.workflow.yaml
│   │   │   ├── procurement.workflow.yaml
│   │   │   ├── project-intake.workflow.yaml
│   │   │   ├── resource-reallocation.workflow.yaml
│   │   │   ├── risk-mitigation.workflow.yaml
│   │   │   └── vendor-onboarding.workflow.yaml
│   │   ├── environments
│   │   │   ├── dev.yaml
│   │   │   ├── prod.yaml
│   │   │   └── test.yaml
│   │   ├── feature-flags
│   │   │   └── flags.yaml
│   │   ├── human_review.yaml
│   │   ├── iam
│   │   │   └── role-mapping.yaml
│   │   ├── maturity_model.yaml
│   │   ├── plans
│   │   │   └── example_plan.yaml
│   │   ├── pricing.yaml
│   │   ├── rbac
│   │   │   ├── field-level.yaml
│   │   │   ├── permissions.yaml
│   │   │   └── roles.yaml
│   │   ├── retention
│   │   │   └── policies.yaml
│   │   ├── security
│   │   │   └── dlp-policies.yaml
│   │   ├── signing
│   │   │   └── dev_signing_public.pem
│   │   ├── tenants
│   │   │   ├── README.md
│   │   │   └── default.yaml
│   │   └── vector_store.yaml
│   ├── docker
│   │   ├── docker-compose-demo.yml
│   │   ├── docker-compose.test.yml
│   │   └── docker-compose.yml
│   ├── infra
│   │   ├── README.md
│   │   ├── kubernetes
│   │   │   ├── README.md
│   │   │   ├── db-backup-cronjob.yaml
│   │   │   ├── db-backup-scripts.yaml
│   │   │   ├── db-backup-secret.yaml
│   │   │   ├── deployment.yaml
│   │   │   ├── helm-charts
│   │   │   │   ├── README.md
│   │   │   │   ├── observability
│   │   │   │   │   ├── Chart.yaml
│   │   │   │   │   ├── templates
│   │   │   │   │   │   ├── configmap.yaml
│   │   │   │   │   │   ├── deployment.yaml
│   │   │   │   │   │   └── service.yaml
│   │   │   │   │   └── values.yaml
│   │   │   │   └── ppm-platform
│   │   │   │       ├── Chart.yaml
│   │   │   │       ├── values-template.yaml
│   │   │   │       └── values.yaml
│   │   │   ├── manifests
│   │   │   │   ├── README.md
│   │   │   │   ├── backup-jobs.yaml
│   │   │   │   ├── cert-manager-issuer.yaml
│   │   │   │   ├── istio-mtls.yaml
│   │   │   │   ├── namespace.yaml
│   │   │   │   ├── network-policies.yaml
│   │   │   │   ├── pod-security.yaml
│   │   │   │   └── resource-quotas.yaml
│   │   │   ├── secret-provider-class.yaml
│   │   │   ├── secret-rotation-cronjob.yaml
│   │   │   ├── secret-rotation-scripts.yaml
│   │   │   ├── secrets.yaml.example
│   │   │   └── service-account.yaml
│   │   ├── observability
│   │   │   ├── README.md
│   │   │   ├── alerts
│   │   │   │   ├── README.md
│   │   │   │   └── ppm-alerts.yaml
│   │   │   ├── dashboards
│   │   │   │   ├── README.md
│   │   │   │   ├── ppm-error-budget.json
│   │   │   │   ├── ppm-platform.json
│   │   │   │   └── ppm-slo.json
│   │   │   ├── otel
│   │   │   │   ├── README.md
│   │   │   │   ├── collector.yaml
│   │   │   │   └── helm
│   │   │   │       ├── Chart.yaml
│   │   │   │       ├── templates
│   │   │   │       │   ├── configmap.yaml
│   │   │   │       │   ├── deployment.yaml
│   │   │   │       │   ├── secretproviderclass.yaml
│   │   │   │       │   ├── service.yaml
│   │   │   │       │   └── serviceaccount.yaml
│   │   │   │       └── values.yaml
│   │   │   └── slo
│   │   │       └── ppm-slo.yaml
│   │   ├── policies
│   │   │   ├── README.md
│   │   │   ├── dlp
│   │   │   │   ├── README.md
│   │   │   │   └── bundles
│   │   │   │       ├── credentials.rego
│   │   │   │       ├── default-dlp-policy-bundle.yaml
│   │   │   │       └── pii.rego
│   │   │   ├── network
│   │   │   │   ├── README.md
│   │   │   │   └── bundles
│   │   │   │       └── default-network-policy-bundle.yaml
│   │   │   ├── schema
│   │   │   │   └── policy-bundle.schema.json
│   │   │   └── security
│   │   │       ├── README.md
│   │   │       └── bundles
│   │   │           └── default-security-policy-bundle.yaml
│   │   ├── tenancy
│   │   │   ├── deprovision_tenant.sh
│   │   │   └── provision_tenant.sh
│   │   └── terraform
│   │       ├── README.md
│   │       ├── dr
│   │       │   ├── README.md
│   │       │   ├── failover.sh
│   │       │   └── restore.sh
│   │       ├── envs
│   │       │   ├── README.md
│   │       │   ├── demo
│   │       │   │   ├── main.tf
│   │       │   │   ├── outputs.tf
│   │       │   │   ├── terraform.tfvars.example
│   │       │   │   ├── variables.tf
│   │       │   │   └── versions.tf
│   │       │   ├── dev
│   │       │   │   ├── README.md
│   │       │   │   ├── main.tf
│   │       │   │   └── terraform.tfvars
│   │       │   ├── prod
│   │       │   │   ├── README.md
│   │       │   │   ├── backend.tfvars
│   │       │   │   └── terraform.tfvars
│   │       │   ├── stage
│   │       │   │   ├── README.md
│   │       │   │   └── terraform.tfvars
│   │       │   └── test
│   │       │       └── README.md
│   │       ├── main.tf
│   │       └── modules
│   │           ├── README.md
│   │           ├── aks
│   │           │   ├── main.tf
│   │           │   ├── outputs.tf
│   │           │   └── variables.tf
│   │           ├── cost-analysis
│   │           │   ├── README.md
│   │           │   ├── main.tf
│   │           │   ├── outputs.tf
│   │           │   └── variables.tf
│   │           ├── keyvault
│   │           │   ├── README.md
│   │           │   ├── main.tf
│   │           │   ├── outputs.tf
│   │           │   └── variables.tf
│   │           ├── monitoring
│   │           │   ├── main.tf
│   │           │   ├── outputs.tf
│   │           │   └── variables.tf
│   │           ├── networking
│   │           │   ├── main.tf
│   │           │   ├── outputs.tf
│   │           │   └── variables.tf
│   │           └── postgresql
│   │               ├── README.md
│   │               ├── main.tf
│   │               ├── outputs.tf
│   │               └── variables.tf
│   ├── requirements
│   │   ├── requirements-demo.txt
│   │   ├── requirements-dev.in
│   │   ├── requirements-dev.txt
│   │   ├── requirements.in
│   │   └── requirements.txt
│   ├── schemas
│   │   ├── README.md
│   │   ├── approval_policies.schema.json
│   │   ├── business-case-settings.schema.json
│   │   ├── intent-router.schema.json
│   │   └── intent-routing.schema.json
│   ├── scripts
│   │   ├── README.md
│   │   ├── build_template_dependency_map.py
│   │   ├── check-docs-migration-guard.py
│   │   ├── check-legacy-ui-references.py
│   │   ├── check-links.py
│   │   ├── check-migrations.py
│   │   ├── check-placeholders.py
│   │   ├── check-schema-example-updates.py
│   │   ├── check-templates.py
│   │   ├── check-ui-emojis.sh
│   │   ├── check-ui-icons.sh
│   │   ├── check_api_versioning.py
│   │   ├── check_placeholders.py
│   │   ├── compare_benchmarks.py
│   │   ├── connector-certification.py
│   │   ├── db_backup.sh
│   │   ├── demo_preflight.py
│   │   ├── export_audit_evidence.py
│   │   ├── fix_docs_formatting.py
│   │   ├── full_platform_demo_run.py
│   │   ├── full_platform_demo_smoke.py
│   │   ├── generate-sbom.py
│   │   ├── generate_agent_metadata.py
│   │   ├── generate_demo_data.py
│   │   ├── init-db.sql
│   │   ├── load-test.py
│   │   ├── load_demo_data.py
│   │   ├── quickstart_smoke.py
│   │   ├── reset_demo_data.sh
│   │   ├── rotate_secrets.sh
│   │   ├── schema_registry.py
│   │   ├── schema_tool.py
│   │   ├── sign-artifact.py
│   │   ├── smoke_test_staging.py
│   │   ├── test_migration_rollback.py
│   │   ├── ui_coverage_check.py
│   │   ├── validate-analytics-jobs.py
│   │   ├── validate-connector-sandbox.py
│   │   ├── validate-examples.py
│   │   ├── validate-github-workflows.py
│   │   ├── validate-helm-charts.py
│   │   ├── validate-intent-routing.py
│   │   ├── validate-manifests.py
│   │   ├── validate-mcp-manifests.py
│   │   ├── validate-policies.py
│   │   ├── validate-schemas.py
│   │   ├── validate-workflows.py
│   │   ├── validate_config.py
│   │   ├── validate_demo_fixtures.py
│   │   ├── verify-production-readiness.sh
│   │   ├── verify-signature.py
│   │   └── verify_manifest.py
│   ├── smoke_workspace_wiring.py
│   └── tools
│       ├── README.md
│       ├── __init__.py
│       ├── agent_runner.py
│       ├── agent_runner_core.py
│       ├── check_config_parity.py
│       ├── check_connector_maturity.py
│       ├── check_observability_compliance.py
│       ├── check_root_layout.py
│       ├── check_secret_source_policy.py
│       ├── check_security_middleware.py
│       ├── codegen
│       │   ├── README.md
│       │   ├── __init__.py
│       │   ├── codegen_config.yaml
│       │   ├── generate_docs.py
│       │   └── run.py
│       ├── collect_maturity_score.py
│       ├── component_runner.py
│       ├── config_validator.py
│       ├── connector_runner.py
│       ├── env_validate.py
│       ├── format
│       │   ├── README.md
│       │   ├── __init__.py
│       │   ├── format_config.yaml
│       │   └── run.py
│       ├── lint
│       │   ├── README.md
│       │   ├── __init__.py
│       │   ├── lint_config.yaml
│       │   └── run.py
│       ├── load_testing
│       │   ├── __init__.py
│       │   └── runner.py
│       ├── local-dev
│       │   ├── README.md
│       │   ├── dev_down.sh
│       │   ├── dev_up.sh
│       │   └── docker-compose.override.example.yml
│       ├── observability_compliance_checks.py
│       ├── release_gate.py
│       ├── run_bandit.py
│       ├── run_dast.py
│       ├── runtime_paths.py
│       └── security_baseline_checks.py
├── packages
│   ├── README.md
│   ├── agent-sdk
│   │   ├── README.md
│   │   └── src
│   │       ├── __init__.py
│   │       ├── context.py
│   │       ├── custom_agent.py
│   │       ├── manifest.py
│   │       ├── sandbox.py
│   │       └── testing.py
│   ├── canvas-engine
│   │   ├── .eslintrc.cjs
│   │   ├── README.md
│   │   ├── docs
│   │   │   └── document-canvas-editor-migration.md
│   │   ├── package.json
│   │   ├── src
│   │   │   ├── components
│   │   │   │   ├── ApprovalCanvas
│   │   │   │   │   ├── ApprovalCanvas.module.css
│   │   │   │   │   ├── ApprovalCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── BacklogCanvas
│   │   │   │   │   ├── BacklogCanvas.module.css
│   │   │   │   │   ├── BacklogCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── BoardCanvas
│   │   │   │   │   ├── BoardCanvas.module.css
│   │   │   │   │   ├── BoardCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── CanvasHost
│   │   │   │   │   ├── CanvasHost.module.css
│   │   │   │   │   ├── CanvasHost.tsx
│   │   │   │   │   ├── TabBar.module.css
│   │   │   │   │   ├── TabBar.tsx
│   │   │   │   │   ├── Toolbar.module.css
│   │   │   │   │   ├── Toolbar.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── DashboardCanvas
│   │   │   │   │   ├── DashboardCanvas.module.css
│   │   │   │   │   ├── DashboardCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── DependencyMapCanvas
│   │   │   │   │   ├── DependencyMapCanvas.module.css
│   │   │   │   │   ├── DependencyMapCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── DocumentCanvas
│   │   │   │   │   ├── DocumentCanvas.editor.test.tsx
│   │   │   │   │   ├── DocumentCanvas.module.css
│   │   │   │   │   ├── DocumentCanvas.security.test.tsx
│   │   │   │   │   ├── DocumentCanvas.tsx
│   │   │   │   │   ├── index.ts
│   │   │   │   │   └── richTextAdapter.ts
│   │   │   │   ├── FinancialCanvas
│   │   │   │   │   ├── FinancialCanvas.module.css
│   │   │   │   │   ├── FinancialCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── GanttCanvas
│   │   │   │   │   ├── GanttCanvas.module.css
│   │   │   │   │   ├── GanttCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── GridCanvas
│   │   │   │   │   ├── GridCanvas.module.css
│   │   │   │   │   ├── GridCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── RoadmapCanvas
│   │   │   │   │   ├── RoadmapCanvas.module.css
│   │   │   │   │   ├── RoadmapCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── SpreadsheetCanvas
│   │   │   │   │   ├── SpreadsheetCanvas.module.css
│   │   │   │   │   ├── SpreadsheetCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── StructuredTreeCanvas
│   │   │   │   │   ├── StructuredTreeCanvas.module.css
│   │   │   │   │   ├── StructuredTreeCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   ├── TimelineCanvas
│   │   │   │   │   ├── TimelineCanvas.module.css
│   │   │   │   │   ├── TimelineCanvas.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   └── index.ts
│   │   │   ├── global.d.ts
│   │   │   ├── hooks
│   │   │   │   ├── index.ts
│   │   │   │   └── useCanvasHost.ts
│   │   │   ├── index.ts
│   │   │   ├── security
│   │   │   │   ├── SANITIZATION_POLICY.md
│   │   │   │   ├── htmlSanitizer.test.ts
│   │   │   │   ├── htmlSanitizer.ts
│   │   │   │   └── index.ts
│   │   │   ├── test
│   │   │   │   └── setup.ts
│   │   │   └── types
│   │   │       ├── artifact.test.ts
│   │   │       ├── artifact.ts
│   │   │       ├── canvas.test.ts
│   │   │       ├── canvas.ts
│   │   │       └── index.ts
│   │   ├── tsconfig.json
│   │   └── vitest.config.ts
│   ├── common
│   │   ├── README.md
│   │   └── src
│   │       └── common
│   │           ├── __init__.py
│   │           ├── bootstrap.py
│   │           ├── env_validation.py
│   │           ├── exceptions.py
│   │           └── resilience.py
│   ├── connectors
│   │   ├── __init__.py
│   │   └── base_connector.py
│   ├── contracts
│   │   ├── README.md
│   │   └── src
│   │       ├── api
│   │       │   ├── __init__.py
│   │       │   └── governance.py
│   │       ├── auth
│   │       │   └── __init__.py
│   │       ├── data
│   │       │   └── __init__.py
│   │       ├── events
│   │       │   ├── __init__.py
│   │       │   └── definitions.py
│   │       └── models
│   │           └── __init__.py
│   ├── crypto
│   │   ├── README.md
│   │   └── src
│   │       └── crypto
│   │           ├── __init__.py
│   │           ├── encryption.py
│   │           ├── hashing.py
│   │           ├── key_derivation.py
│   │           └── signatures.py
│   ├── data-quality
│   │   ├── README.md
│   │   └── src
│   │       └── data_quality
│   │           ├── __init__.py
│   │           ├── helpers.py
│   │           ├── remediation.py
│   │           ├── rules.py
│   │           └── schema_validation.py
│   ├── design-tokens
│   │   ├── README.md
│   │   ├── package.json
│   │   ├── tokens.css
│   │   ├── tokens.json
│   │   └── tokens.ts
│   ├── event-bus
│   │   ├── README.md
│   │   └── src
│   │       └── event_bus
│   │           ├── __init__.py
│   │           ├── models.py
│   │           └── service_bus.py
│   ├── feature-flags
│   │   ├── README.md
│   │   └── src
│   │       └── feature_flags
│   │           ├── __init__.py
│   │           └── manager.py
│   ├── feedback
│   │   ├── __init__.py
│   │   └── feedback_models.py
│   ├── llm
│   │   ├── README.md
│   │   ├── prompt_sanitizer.py
│   │   ├── src
│   │   │   ├── llm
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py
│   │   │   │   ├── router.py
│   │   │   │   └── types.py
│   │   │   ├── model_registry.py
│   │   │   ├── providers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── anthropic_provider.py
│   │   │   │   ├── azure_openai_provider.py
│   │   │   │   ├── google_provider.py
│   │   │   │   └── openai_provider.py
│   │   │   └── router.py
│   │   └── tests
│   │       ├── test_azure_openai_provider.py
│   │       ├── test_gateway.py
│   │       └── test_model_registry_router.py
│   ├── memory_client.py
│   ├── methodology-engine
│   │   ├── README.md
│   │   └── src
│   │       ├── __init__.py
│   │       └── methodology_engine.py
│   ├── observability
│   │   ├── README.md
│   │   └── src
│   │       ├── observability
│   │       │   ├── __init__.py
│   │       │   ├── logging.py
│   │       │   ├── metrics.py
│   │       │   ├── telemetry.py
│   │       │   └── tracing.py
│   │       └── opentelemetry
│   │           ├── __init__.py
│   │           ├── _logs.py
│   │           ├── exporter
│   │           │   ├── __init__.py
│   │           │   └── otlp
│   │           │       ├── __init__.py
│   │           │       └── proto
│   │           │           ├── __init__.py
│   │           │           └── http
│   │           │               ├── __init__.py
│   │           │               ├── _log_exporter.py
│   │           │               ├── metric_exporter.py
│   │           │               └── trace_exporter.py
│   │           ├── metrics.py
│   │           ├── propagate.py
│   │           ├── sdk
│   │           │   ├── __init__.py
│   │           │   ├── _logs
│   │           │   │   ├── __init__.py
│   │           │   │   └── export
│   │           │   │       └── __init__.py
│   │           │   ├── metrics
│   │           │   │   ├── __init__.py
│   │           │   │   └── export
│   │           │   │       └── __init__.py
│   │           │   ├── resources.py
│   │           │   └── trace
│   │           │       ├── __init__.py
│   │           │       └── export
│   │           │           └── __init__.py
│   │           └── trace
│   │               ├── __init__.py
│   │               └── propagation
│   │                   ├── __init__.py
│   │                   └── tracecontext.py
│   ├── policy
│   │   ├── README.md
│   │   └── src
│   │       ├── __init__.py
│   │       └── policy.py
│   ├── security
│   │   ├── README.md
│   │   └── src
│   │       └── security
│   │           ├── __init__.py
│   │           ├── api_governance.py
│   │           ├── audit_log.py
│   │           ├── auth.py
│   │           ├── config.py
│   │           ├── crypto.py
│   │           ├── dlp.py
│   │           ├── errors.py
│   │           ├── headers.py
│   │           ├── iam.py
│   │           ├── keyvault.py
│   │           ├── lineage.py
│   │           ├── prompt_safety.py
│   │           └── secrets.py
│   ├── testing
│   │   ├── README.md
│   │   └── src
│   │       └── testing
│   │           ├── __init__.py
│   │           ├── assertions.py
│   │           ├── fixtures.py
│   │           └── mock_builders.py
│   ├── ui-kit
│   │   ├── README.md
│   │   ├── design-system
│   │   │   ├── README.md
│   │   │   ├── icons
│   │   │   │   ├── README.md
│   │   │   │   └── icon-map.json
│   │   │   ├── stories
│   │   │   │   ├── Button.stories.tsx
│   │   │   │   ├── EmptyState.stories.tsx
│   │   │   │   └── TokenPalette.stories.tsx
│   │   │   └── tokens
│   │   │       ├── design-system-tokens.json
│   │   │       ├── tokens.css
│   │   │       └── tokens.ts
│   │   ├── package.json
│   │   └── src
│   │       └── __init__.py
│   ├── vector_store
│   │   ├── __init__.py
│   │   └── faiss_store.py
│   ├── version.py
│   └── workflow
│       ├── README.md
│       └── src
│           └── workflow
│               ├── __init__.py
│               ├── aggregation.py
│               ├── celery_app.py
│               ├── dispatcher.py
│               ├── executor.py
│               └── tasks.py
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
├── pyproject.toml
├── requirements.txt
├── services
│   ├── README.md
│   ├── __init__.py
│   ├── agent-config
│   │   ├── README.md
│   │   └── src
│   │       ├── __init__.py
│   │       ├── agent_config_service.py
│   │       └── main.py
│   ├── agent-runtime
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── README.md
│   │   │   ├── config
│   │   │   │   └── intent-routing.yaml
│   │   │   ├── main.py
│   │   │   └── runtime.py
│   │   └── tests
│   │       ├── test_agent_runtime_service.py
│   │       ├── test_connector_action_client.py
│   │       └── test_runtime_event_bus.py
│   ├── audit-log
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── contracts
│   │   │   └── openapi.yaml
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   ├── secretproviderclass.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   └── serviceaccount.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── audit_storage.py
│   │   │   ├── main.py
│   │   │   └── retention_job.py
│   │   ├── storage
│   │   │   └── README.md
│   │   └── tests
│   │       ├── test_audit_log.py
│   │       └── test_retention_job.py
│   ├── auth-service
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── auth.py
│   │   │   └── main.py
│   │   └── tests
│   │       └── test_auth_service.py
│   ├── data-lineage-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   └── serviceaccount.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── main.py
│   │   │   ├── quality.py
│   │   │   ├── retention_scheduler.py
│   │   │   └── storage.py
│   │   └── tests
│   │       └── test_lineage_service.py
│   ├── data-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   ├── service.yaml
│   │   │   │   └── serviceaccount.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── main.py
│   │   │   ├── retention_scheduler.py
│   │   │   ├── schema_compatibility.py
│   │   │   └── storage.py
│   │   └── tests
│   │       ├── test_data_service.py
│   │       └── test_schema_governance.py
│   ├── data-sync-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── contracts
│   │   │   └── openapi.yaml
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── rules
│   │   │   ├── README.md
│   │   │   └── default-sync.yaml
│   │   ├── src
│   │   │   ├── conflict_store.py
│   │   │   ├── data_sync_queue.py
│   │   │   ├── data_sync_status.py
│   │   │   ├── jira_client.py
│   │   │   ├── jira_tasks_sync.py
│   │   │   ├── lineage_client.py
│   │   │   ├── main.py
│   │   │   ├── propagation.py
│   │   │   ├── sync_log_store.py
│   │   │   ├── sync_registry.py
│   │   │   └── task_store.py
│   │   └── tests
│   │       ├── test_data_sync.py
│   │       └── test_data_sync_service.py
│   ├── feedback_service.py
│   ├── identity-access
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── contracts
│   │   │   └── openapi.yaml
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── main.py
│   │   │   ├── saml.py
│   │   │   ├── scim_models.py
│   │   │   └── scim_store.py
│   │   ├── storage
│   │   │   └── scim.db
│   │   └── tests
│   │       ├── test_identity_access.py
│   │       └── test_scim.py
│   ├── memory_service
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── memory_service.py
│   ├── notification-service
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── contracts
│   │   │   └── openapi.yaml
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── src
│   │   │   └── main.py
│   │   ├── templates
│   │   │   ├── README.md
│   │   │   ├── agent-run-status.txt
│   │   │   ├── intake-triage-summary.txt
│   │   │   ├── portfolio-intake.txt
│   │   │   └── welcome.txt
│   │   └── tests
│   │       └── test_notification_service.py
│   ├── policy-engine
│   │   ├── .dockerignore
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── contracts
│   │   │   └── openapi.yaml
│   │   ├── helm
│   │   │   ├── Chart.yaml
│   │   │   ├── README.md
│   │   │   ├── templates
│   │   │   │   ├── _helpers.tpl
│   │   │   │   ├── certificate.yaml
│   │   │   │   ├── configmap.yaml
│   │   │   │   ├── deployment.yaml
│   │   │   │   ├── hpa.yaml
│   │   │   │   ├── ingress.yaml
│   │   │   │   ├── pdb.yaml
│   │   │   │   └── service.yaml
│   │   │   └── values.yaml
│   │   ├── main.py
│   │   ├── policies
│   │   │   ├── README.md
│   │   │   ├── bundles
│   │   │   │   └── default-policy-bundle.yaml
│   │   │   └── schema
│   │   │       └── policy-bundle.schema.json
│   │   ├── src
│   │   │   ├── main.py
│   │   │   └── policy_config.py
│   │   └── tests
│   │       └── test_policy_engine.py
│   ├── realtime-coedit-service
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── main.py
│   │   ├── src
│   │   │   ├── annotation_routes.py
│   │   │   ├── annotations.py
│   │   │   ├── main.py
│   │   │   └── storage.py
│   │   └── tests
│   │       └── test_realtime_coedit_service.py
│   ├── scope_baseline
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── scope_baseline_service.py
│   └── telemetry-service
│       ├── .dockerignore
│       ├── Dockerfile
│       ├── README.md
│       ├── contracts
│       │   └── openapi.yaml
│       ├── helm
│       │   ├── Chart.yaml
│       │   ├── README.md
│       │   ├── files
│       │   │   └── collector.yaml
│       │   ├── templates
│       │   │   ├── _helpers.tpl
│       │   │   ├── certificate.yaml
│       │   │   ├── collector-config.yaml
│       │   │   ├── configmap.yaml
│       │   │   ├── deployment.yaml
│       │   │   ├── hpa.yaml
│       │   │   ├── ingress.yaml
│       │   │   ├── pdb.yaml
│       │   │   └── service.yaml
│       │   └── values.yaml
│       ├── main.py
│       ├── pipelines
│       │   └── README.md
│       ├── src
│       │   ├── main.py
│       │   └── otel.py
│       └── tests
│           ├── test_telemetry.py
│           └── test_telemetry_service.py
├── tests
│   ├── README.md
│   ├── agents
│   │   ├── test_analytics_insights_agent.py
│   │   ├── test_approval_workflow_agent.py
│   │   ├── test_business_case.py
│   │   ├── test_business_case_investment_agent.py
│   │   ├── test_change_configuration_agent.py
│   │   ├── test_compliance_regulatory_agent.py
│   │   ├── test_continuous_improvement.py
│   │   ├── test_data_sync_agent.py
│   │   ├── test_delegation.py
│   │   ├── test_demand_intake_agent.py
│   │   ├── test_demo_mode.py
│   │   ├── test_distributed_workflow_engine.py
│   │   ├── test_financial_management_agent.py
│   │   ├── test_intent_router.py
│   │   ├── test_intent_router_agent.py
│   │   ├── test_knowledge_document.py
│   │   ├── test_knowledge_management_agent.py
│   │   ├── test_portfolio_strategy_agent.py
│   │   ├── test_process_mining_agent.py
│   │   ├── test_program_management_agent.py
│   │   ├── test_project_definition.py
│   │   ├── test_project_definition_agent.py
│   │   ├── test_project_lifecycle_agent.py
│   │   ├── test_quality_management_agent.py
│   │   ├── test_release_deployment_agent.py
│   │   ├── test_resource_capacity_agent.py
│   │   ├── test_response_orchestration.py
│   │   ├── test_response_orchestration_agent.py
│   │   ├── test_risk_adjusted_planning.py
│   │   ├── test_risk_management_agent.py
│   │   ├── test_schedule_planning_agent.py
│   │   ├── test_stakeholder_comm_agent.py
│   │   ├── test_stakeholder_communications_agent.py
│   │   ├── test_system_health_agent.py
│   │   ├── test_vendor_procurement_agent.py
│   │   ├── test_web_search.py
│   │   └── test_workflow_engine_agent.py
│   ├── apps
│   │   ├── test_agents_route_errors.py
│   │   ├── test_api_gateway_health.py
│   │   ├── test_certifications_api.py
│   │   ├── test_document_session_store_concurrency.py
│   │   ├── test_methodology_relationship_defaults.py
│   │   ├── test_orchestration_service.py
│   │   ├── test_web_governance_api.py
│   │   └── test_web_legacy_route_redirects.py
│   ├── config
│   │   ├── test_config_validator.py
│   │   └── test_connector_maturity_policy.py
│   ├── conftest.py
│   ├── connectors
│   │   ├── __init__.py
│   │   ├── connector_test_harness.py
│   │   ├── test_base_connector.py
│   │   ├── test_connector_implementations.py
│   │   ├── test_connector_sync_routes.py
│   │   ├── test_connector_webhooks.py
│   │   ├── test_iot_connector.py
│   │   ├── test_mcp_client.py
│   │   ├── test_priority_connector_harness.py
│   │   └── test_regulatory_compliance_connector.py
│   ├── contract
│   │   ├── README.md
│   │   ├── api-gateway-openapi.json
│   │   ├── test_api_contract.py
│   │   └── test_service_api_governance.py
│   ├── data
│   │   └── test_demo_data.py
│   ├── demo
│   │   ├── test_demo_fixtures_present.py
│   │   └── test_ui_data_completeness.py
│   ├── docs
│   │   └── test_realtime_coedit.py
│   ├── e2e
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── test_acceptance_scenarios.py
│   │   ├── test_connector_webhooks.py
│   │   ├── test_user_journey.py
│   │   ├── test_web_canvas_flow.py
│   │   └── test_web_login.py
│   ├── feedback
│   │   └── test_feedback.py
│   ├── helpers
│   │   └── service_bus.py
│   ├── integration
│   │   ├── README.md
│   │   ├── conftest.py
│   │   ├── connectors
│   │   │   ├── test_azure_devops_connector.py
│   │   │   ├── test_jira_connector.py
│   │   │   ├── test_planview_connector.py
│   │   │   ├── test_servicenow_connector.py
│   │   │   └── test_sync_job.py
│   │   ├── test_ai_models.py
│   │   ├── test_analytics.py
│   │   ├── test_analytics_kpi_engine.py
│   │   ├── test_circuit_breaker.py
│   │   ├── test_connector_framework.py
│   │   ├── test_data_lineage_service.py
│   │   ├── test_data_migrations.py
│   │   ├── test_data_service_clients.py
│   │   ├── test_end_to_end_workflow.py
│   │   ├── test_event_bus.py
│   │   ├── test_mcp_connector_routing.py
│   │   ├── test_mcp_sync_flows.py
│   │   ├── test_mock_connectors.py
│   │   ├── test_multi_agent_flows.py
│   │   ├── test_orchestration_service_orchestrator_persistence_suite.py
│   │   ├── test_orchestration_workflow_integration.py
│   │   ├── test_orchestrator_persistence.py
│   │   ├── test_orchestrator_readiness_integration.py
│   │   ├── test_persistence.py
│   │   ├── test_plan_approval.py
│   │   ├── test_portfolio_program_agent_integration.py
│   │   ├── test_service_bus_event_bus_integration.py
│   │   ├── test_workflow_agent_execution.py
│   │   ├── test_workflow_celery_execution.py
│   │   ├── test_workflow_compensation.py
│   │   ├── test_workflow_definition_validation.py
│   │   ├── test_workflow_definitions_suite.py
│   │   ├── test_workflow_engine_runtime.py
│   │   ├── test_workflow_parallel_and_loop.py
│   │   ├── test_workflow_retry.py
│   │   ├── test_workflow_runtime_suite.py
│   │   └── test_workflow_storage_suite.py
│   ├── llm
│   │   ├── test_prompt_sanitizer.py
│   │   └── test_prompt_sanitizer_enhanced.py
│   ├── load
│   │   ├── README.md
│   │   ├── multi_agent_scenarios.py
│   │   ├── sla_targets.json
│   │   ├── test_connectors_latency_sla.py
│   │   └── test_load_sla.py
│   ├── memory
│   │   └── test_memory_service.py
│   ├── notification
│   │   └── test_localization.py
│   ├── observability
│   │   ├── test_business_workflow_metrics.py
│   │   ├── test_correlation.py
│   │   ├── test_cost_tracking.py
│   │   └── test_observability_compliance.py
│   ├── ops
│   │   ├── fixtures
│   │   │   └── check_placeholders
│   │   │       ├── invalid
│   │   │       │   ├── apps
│   │   │       │   │   └── demo-app
│   │   │       │   │       └── README.md
│   │   │       │   └── services
│   │   │       │       └── demo-service
│   │   │       │           └── README.md
│   │   │       └── valid
│   │   │           ├── apps
│   │   │           │   └── demo-app
│   │   │           │       └── README.md
│   │   │           └── services
│   │   │               └── demo-service
│   │   │                   └── README.md
│   │   ├── test_check_placeholders.py
│   │   ├── test_observability_compliance.py
│   │   └── tools
│   │       └── test_check_root_layout.py
│   ├── orchestrator
│   │   └── test_human_review.py
│   ├── packages
│   │   ├── common
│   │   │   ├── test_exceptions_package.py
│   │   │   └── test_resilience_package.py
│   │   └── security
│   │       ├── conftest.py
│   │       ├── test_auth_package.py
│   │       ├── test_crypto_package.py
│   │       ├── test_dlp_package.py
│   │       └── test_prompt_safety_package.py
│   ├── performance
│   │   ├── README.md
│   │   ├── baselines.json
│   │   ├── config.yaml
│   │   ├── locustfile.py
│   │   ├── mock_server.py
│   │   ├── quick_config.yaml
│   │   ├── report_summary.py
│   │   ├── run_locust.py
│   │   └── test_event_bus_load.py
│   ├── policies
│   │   ├── test_dlp_rego.py
│   │   ├── test_rbac_abac_policies.py
│   │   └── validate_policies_test.py
│   ├── prompts
│   │   └── test_prompt_registry.py
│   ├── runtime
│   │   ├── test_eval_harness.py
│   │   ├── test_orchestrator.py
│   │   ├── test_service_bus_event_bus.py
│   │   └── test_template_workflow.py
│   ├── security
│   │   ├── README.md
│   │   ├── test_agent_config_rbac.py
│   │   ├── test_auth_cache.py
│   │   ├── test_auth_rbac.py
│   │   ├── test_compliance.py
│   │   ├── test_dast_integration.py
│   │   ├── test_dlp_and_encryption.py
│   │   ├── test_downstream_auth.py
│   │   ├── test_field_level_masking.py
│   │   ├── test_field_masking.py
│   │   ├── test_jwt_delegation.py
│   │   ├── test_key_rotation.py
│   │   ├── test_lineage_masking.py
│   │   ├── test_oidc_cache.py
│   │   ├── test_policy_engine_integration.py
│   │   ├── test_rate_limit_cors.py
│   │   ├── test_retention_config.py
│   │   ├── test_secret_resolution.py
│   │   ├── test_secret_resolution_and_rbac.py
│   │   ├── test_security_baseline_compliance.py
│   │   └── test_security_headers.py
│   ├── services
│   │   ├── test_agent_config_service.py
│   │   └── test_scope_baseline_service.py
│   ├── test_api.py
│   ├── test_approval_workflow.py
│   ├── test_artifact_validation.py
│   ├── test_backup_runbook.py
│   ├── test_base_agent.py
│   ├── test_data_quality_pipeline.py
│   ├── test_data_quality_rules.py
│   ├── test_event_contracts.py
│   ├── test_intent_router.py
│   ├── test_mcp_connector_exception_handling.py
│   ├── test_operational_runbooks.py
│   ├── test_resilience_middleware.py
│   ├── test_schema_registry_tooling.py
│   ├── test_schema_validation.py
│   ├── test_security_review_fixes.py
│   ├── tools
│   │   ├── test_agent_metadata_generation.py
│   │   ├── test_component_discovery.py
│   │   └── test_runtime_paths.py
│   ├── unit
│   │   ├── _route_test_helpers.py
│   │   ├── test_annotations.py
│   │   ├── test_briefing_renderer.py
│   │   ├── test_briefing_service.py
│   │   ├── test_capacity_planning.py
│   │   ├── test_cross_feature_integration.py
│   │   ├── test_execution_events.py
│   │   ├── test_health_aggregator.py
│   │   ├── test_intake_intelligence.py
│   │   ├── test_intake_to_project.py
│   │   ├── test_knowledge_graph_service.py
│   │   ├── test_llm_helpers.py
│   │   ├── test_nl_workflow.py
│   │   ├── test_predictive.py
│   │   ├── test_project_setup.py
│   │   └── test_security_posture.py
│   └── vector_store
│       └── test_faiss_store.py
├── tools
│   ├── __init__.py
│   ├── component_runner.py
│   └── runtime_paths.py
└── vendor
    ├── __init__.py
    ├── celery
    │   └── __init__.py
    ├── jinja2
    │   └── __init__.py
    ├── jsonschema
    │   └── __init__.py
    ├── multipart
    │   ├── __init__.py
    │   └── multipart.py
    ├── numpy
    │   └── __init__.py
    ├── slowapi
    │   ├── __init__.py
    │   ├── errors.py
    │   ├── middleware.py
    │   └── util.py
    ├── sqlalchemy
    │   ├── __init__.py
    │   ├── engine
    │   │   └── __init__.py
    │   ├── exc.py
    │   ├── ext
    │   │   ├── __init__.py
    │   │   └── asyncio
    │   │       └── __init__.py
    │   ├── orm
    │   │   └── __init__.py
    │   └── sql
    │       └── __init__.py
    └── stubs
        ├── __init__.py
        ├── email_validator.py
        ├── events.py
        ├── prompt_registry.py
        ├── pydantic_settings.py
        ├── redis
        │   ├── __init__.py
        │   └── asyncio.py
        ├── requests.py
        └── runtime_flags.py
```
