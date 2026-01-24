# Tests

Comprehensive test suite for the Multi-Agent PPM Platform.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_base_agent.py

# Run specific test
pytest tests/test_intent_router.py::test_portfolio_query_classification

# Run tests in parallel
pytest -n auto
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_base_agent.py       # Base agent tests
├── test_intent_router.py    # Intent Router agent tests
├── test_api.py              # API endpoint tests
├── unit/                    # Unit tests
├── integration/             # Integration tests
└── e2e/                     # End-to-end tests
```

## Test Coverage

We aim for >80% code coverage. Current coverage can be viewed in the CI/CD pipeline.

## Writing Tests

### Unit Tests

Test individual components in isolation:

```python
@pytest.mark.asyncio
async def test_agent_function():
    agent = MyAgent()
    result = await agent.process({"data": "test"})
    assert result["success"] is True
```

### Integration Tests

Test interactions between components:

```python
@pytest.mark.asyncio
async def test_agent_integration(orchestrator):
    result = await orchestrator.process_query("test query")
    assert result["success"] is True
```

### Fixtures

Common fixtures are defined in `conftest.py`:

- `orchestrator`: Initialized AgentOrchestrator instance
- `mock_azure_openai`: Mock Azure OpenAI client
- `mock_database`: Mock database connection
- `mock_redis`: Mock Redis connection

## Test Requirements

Install test dependencies:

```bash
pip install -e .[dev]
```

This includes:
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock
- httpx (for API testing)
