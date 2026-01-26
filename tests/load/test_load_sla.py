from __future__ import annotations

import time

from fastapi.testclient import TestClient


def test_healthz_latency_sla(auth_headers) -> None:
    from api.main import app

    client = TestClient(app)
    durations = []
    for _ in range(20):
        start = time.perf_counter()
        response = client.get("/healthz", headers=auth_headers)
        assert response.status_code == 200
        durations.append(time.perf_counter() - start)

    average = sum(durations) / len(durations)
    assert average < 0.5
