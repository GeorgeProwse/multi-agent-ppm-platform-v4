import pytest

from stakeholder_communications_agent import StakeholderCommunicationsAgent


@pytest.mark.asyncio
async def test_sentiment_analysis_triggers_alert(tmp_path, monkeypatch):
    agent = StakeholderCommunicationsAgent(
        config={"stakeholder_store_path": tmp_path / "stakeholders.json"}
    )
    await agent.initialize()

    registration = await agent.process(
        {
            "action": "register_stakeholder",
            "tenant_id": "tenant-alerts",
            "stakeholder": {
                "name": "Avery Lane",
                "email": "avery@example.com",
                "role": "Sponsor",
            },
        }
    )

    async def mock_sentiment(_text):
        return {"score": -0.9, "label": "negative", "confidence": 0.9}

    alert_payloads = []

    async def mock_alert(stakeholder_id, sentiment, feedback_record):
        alert_payloads.append((stakeholder_id, sentiment, feedback_record))

    monkeypatch.setattr(agent, "_analyze_text_sentiment", mock_sentiment)
    monkeypatch.setattr(agent, "_trigger_sentiment_alert", mock_alert)

    feedback = await agent.process(
        {
            "action": "collect_feedback",
            "tenant_id": "tenant-alerts",
            "feedback": {
                "stakeholder_id": registration["stakeholder_id"],
                "project_id": "proj-1",
                "comments": "This is not going well.",
                "rating": 1,
            },
        }
    )

    assert feedback["alert_triggered"] is True
    assert alert_payloads


@pytest.mark.asyncio
async def test_generate_message_uses_openai_draft(tmp_path, monkeypatch):
    agent = StakeholderCommunicationsAgent(
        config={
            "stakeholder_store_path": tmp_path / "stakeholders.json",
            "azure_openai_endpoint": "https://openai.local",
            "azure_openai_api_key": "test-key",
            "azure_openai_deployment": "test-model",
        }
    )
    await agent.initialize()

    async def mock_openai_text(*_args, **_kwargs):
        return {"content": "Draft update", "provider": "azure_openai"}

    monkeypatch.setattr(agent, "_generate_openai_text", mock_openai_text)

    response = await agent.process(
        {
            "action": "generate_message",
            "message": {
                "subject": "Weekly Update",
                "prompt_type": "status_summary",
                "data": {"summary": "On track"},
                "stakeholder_ids": [],
            },
        }
    )

    message = agent.messages[response["message_id"]]
    assert message["content"] == "Draft update"
    assert message["review_required"] is True


@pytest.mark.asyncio
async def test_schedule_event_uses_graph_suggestions(tmp_path, monkeypatch):
    agent = StakeholderCommunicationsAgent(
        config={"stakeholder_store_path": tmp_path / "stakeholders.json"}
    )
    await agent.initialize()

    suggestion_time = "2030-01-01T10:00:00"

    async def mock_suggestions(*_args, **_kwargs):
        return [suggestion_time]

    async def mock_graph_event(event, _attachments):
        return {"event_id": "graph-1", "online_meeting_url": "https://meet", "scheduled_time": suggestion_time}

    monkeypatch.setattr(agent, "_suggest_meeting_times", mock_suggestions)
    monkeypatch.setattr(agent, "_create_graph_event", mock_graph_event)

    response = await agent.process(
        {
            "action": "schedule_event",
            "event": {
                "title": "Stakeholder Sync",
                "duration": 30,
                "stakeholder_ids": [],
            },
        }
    )

    assert response["scheduled_time"] == suggestion_time
    assert response["meeting_suggestions"] == [suggestion_time]
