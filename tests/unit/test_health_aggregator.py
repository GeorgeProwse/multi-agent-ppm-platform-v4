"""Tests for connector health aggregator (Enhancement 4)."""

from __future__ import annotations

from health_aggregator import ConnectorHealthAggregator


def test_get_all_status():
    aggregator = ConnectorHealthAggregator()
    statuses = aggregator.get_all_status("tenant-1")
    assert len(statuses) > 0
    for s in statuses:
        assert s.connector_id
        assert s.status in ("healthy", "degraded", "down")
        assert s.circuit_state in ("closed", "half_open", "open")


def test_get_data_freshness():
    aggregator = ConnectorHealthAggregator()
    freshness = aggregator.get_data_freshness("tenant-1")
    assert len(freshness) > 0
    for f in freshness:
        assert f.freshness_status in ("fresh", "stale", "critical")
        assert f.record_count >= 0


def test_get_conflict_queue():
    aggregator = ConnectorHealthAggregator()
    conflicts = aggregator.get_conflict_queue("tenant-1")
    assert len(conflicts) > 0
    for c in conflicts:
        assert c.conflict_id
        assert c.status == "unresolved"


def test_resolve_conflict():
    aggregator = ConnectorHealthAggregator()
    result = aggregator.resolve_conflict("tenant-1", "cf-001", "accept_source")
    assert result.status == "resolved"
    assert result.resolution == "accept_source"
