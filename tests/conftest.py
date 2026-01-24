"""
Pytest configuration and fixtures for Multi-Agent PPM Platform tests
"""

import asyncio

import pytest


# Configure event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_azure_openai():
    """Mock Azure OpenAI client for testing."""
    # TODO: Implement Azure OpenAI mock
    pass


@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    # TODO: Implement database mock
    pass


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    # TODO: Implement Redis mock
    pass


@pytest.fixture
async def orchestrator():
    """Create and initialize an orchestrator instance for testing."""
    from src.core.orchestration.orchestrator import AgentOrchestrator

    orch = AgentOrchestrator()
    await orch.initialize()

    yield orch

    await orch.cleanup()


@pytest.fixture
def sample_query():
    """Sample query for testing intent routing."""
    return "Show me the budget variance for Project Apollo"


@pytest.fixture
def sample_context():
    """Sample context for testing."""
    return {
        "user_id": "test_user",
        "session_id": "test_session",
        "timestamp": "2024-01-01T00:00:00Z",
    }
