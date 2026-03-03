"""
Action handler for conflict identification:
  - identify_conflicts
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from resource_capacity_agent import ResourceCapacityAgent


async def identify_conflicts(
    agent: ResourceCapacityAgent, filters: dict[str, Any]
) -> dict[str, Any]:
    """
    Identify resource allocation conflicts.

    Returns conflicts and resolution recommendations.
    """
    agent.logger.info("Identifying resource conflicts")

    conflicts = []

    for resource_id in agent.resource_pool.keys():
        resource_allocations = agent._load_allocations(resource_id)
        # Check for overlapping allocations
        for i, alloc1 in enumerate(resource_allocations):
            for alloc2 in resource_allocations[i + 1 :]:
                overlap = await agent._check_allocation_overlap(alloc1, alloc2)

                if overlap.get("has_overlap"):
                    # Calculate over-allocation
                    total_allocation = alloc1.get("allocation_percentage", 0) + alloc2.get(
                        "allocation_percentage", 0
                    )

                    if total_allocation > 100:
                        conflicts.append(
                            {
                                "resource_id": resource_id,
                                "resource_name": agent.resource_pool.get(resource_id, {}).get(
                                    "name"
                                ),
                                "allocation_1": alloc1,
                                "allocation_2": alloc2,
                                "overlap_period": overlap.get("period"),
                                "over_allocation_percentage": total_allocation - 100,
                                "severity": "high" if total_allocation > 150 else "medium",
                            }
                        )

    # Generate resolution recommendations
    recommendations = await agent._generate_conflict_recommendations(conflicts)

    return {
        "total_conflicts": len(conflicts),
        "conflicts": conflicts,
        "recommendations": recommendations,
    }
