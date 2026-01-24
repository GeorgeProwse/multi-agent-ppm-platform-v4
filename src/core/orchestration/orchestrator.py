"""
Agent Orchestrator - Manages agent lifecycle and routing
"""

from typing import Dict, Any, Optional
import logging

from src.agents.core.orchestration.intent_router_agent import IntentRouterAgent
from src.agents.core.orchestration.response_orchestration_agent import ResponseOrchestrationAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Central orchestrator for all PPM agents.

    Manages agent lifecycle, routing, and coordination.
    """

    def __init__(self):
        self.agents = {}
        self.initialized = False
        self.intent_router = None
        self.response_orchestrator = None

    async def initialize(self):
        """Initialize all agents."""
        logger.info("Initializing Agent Orchestrator...")

        # Initialize core orchestration agents
        self.intent_router = IntentRouterAgent()
        await self.intent_router.initialize()
        self.agents["intent-router"] = self.intent_router

        self.response_orchestrator = ResponseOrchestrationAgent()
        await self.response_orchestrator.initialize()
        self.agents["response-orchestration"] = self.response_orchestrator

        # TODO: Initialize other agents
        # self._load_portfolio_agents()
        # self._load_delivery_agents()
        # self._load_governance_agents()
        # self._load_operations_agents()
        # self._load_platform_agents()

        self.initialized = True
        logger.info(f"Orchestrator initialized with {len(self.agents)} agents")

    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user query through the full agent pipeline.

        Args:
            query: User's natural language query
            context: Optional context (user_id, session_id, etc.)

        Returns:
            Final aggregated response
        """
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized")

        # Step 1: Route the query
        intent_result = await self.intent_router.execute({
            "query": query,
            "context": context or {},
        })

        if not intent_result["success"]:
            return {
                "success": False,
                "error": "Failed to route query",
                "details": intent_result,
            }

        # Step 2: Orchestrate response
        orchestration_result = await self.response_orchestrator.execute({
            "routing": intent_result["data"]["routing"],
            "parameters": intent_result["data"]["parameters"],
            "query": query,
        })

        return orchestration_result

    def get_agent(self, agent_id: str):
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def get_agent_count(self) -> int:
        """Get total number of loaded agents."""
        return len(self.agents)

    def list_agents(self) -> list:
        """List all loaded agents."""
        return [
            {
                "agent_id": agent_id,
                "capabilities": agent.get_capabilities(),
            }
            for agent_id, agent in self.agents.items()
        ]

    async def cleanup(self):
        """Clean up all agents."""
        logger.info("Cleaning up orchestrator...")
        for agent_id, agent in self.agents.items():
            try:
                await agent.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up agent {agent_id}: {str(e)}")

        self.agents.clear()
        self.initialized = False
        logger.info("Orchestrator cleanup complete")
