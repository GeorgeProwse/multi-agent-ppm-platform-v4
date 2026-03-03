"""
Action handler for utilization metrics:
  - get_utilization
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def get_utilization(
    agent: ResourceCapacityAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    """
    Get utilization metrics.

    Returns utilization data and trends.
    """
    agent.logger.info("Getting utilization metrics")

    # Calculate utilization for all resources
    utilization_data = []

    for resource_id, resource in agent.resource_pool.items():
        utilization = await agent._calculate_resource_utilization(
            resource_id, filters.get("risk_data")
        )
        utilization_data.append(
            {
                "resource_id": resource_id,
                "resource_name": resource.get("name"),
                "role": resource.get("role"),
                "utilization": utilization,
                "status": await agent._get_utilization_status(utilization),
            }
        )

    # Calculate aggregate metrics
    average_utilization = (
        sum(u["utilization"] for u in utilization_data) / len(utilization_data)
        if utilization_data
        else 0
    )

    over_allocated = [u for u in utilization_data if u["utilization"] > 1.0]
    under_utilized = [u for u in utilization_data if u["utilization"] < 0.5]

    result = {
        "total_resources": len(utilization_data),
        "average_utilization": average_utilization,
        "target_utilization": agent.utilization_target,
        "utilization_variance": average_utilization - agent.utilization_target,
        "over_allocated_count": len(over_allocated),
        "under_utilized_count": len(under_utilized),
        "over_allocated_resources": over_allocated,
        "under_utilized_resources": under_utilized,
        "utilization_by_resource": utilization_data,
    }
    if agent.analytics_client:
        agent.analytics_client.record_metric("utilization.average", average_utilization)
        agent.analytics_client.record_metric("utilization.over_allocated", len(over_allocated))
        agent.analytics_client.record_metric("utilization.under_utilized", len(under_utilized))
    return result
