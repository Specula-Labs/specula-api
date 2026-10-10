"""Regression tests for the canonical /events route path."""

from fastapi.testclient import TestClient

from app import stellar
from app.config import Settings
from app.main import app

client = TestClient(app)
CONTRACT_ID = "C" + "A" * 55


def _stub(monkeypatch):
    monkeypatch.setattr(stellar, "get_settings", lambda: Settings(contract_id=CONTRACT_ID))

    def fake_rpc(method, params, settings):
        if method == "getHealth":
            return {"latestLedger": 100000, "oldestLedger": 80000}
        return {"events": [], "cursor": None}

    monkeypatch.setattr(stellar, "_rpc", fake_rpc)


def test_events_without_trailing_slash_is_served_directly(monkeypatch):
    _stub(monkeypatch)
    response = client.get("/events", follow_redirects=False)
    assert response.status_code == 200


def test_events_with_trailing_slash_redirects(monkeypatch):
    _stub(monkeypatch)
    response = client.get("/events/", follow_redirects=False)
    assert response.status_code in (200, 307)
    if response.status_code == 307:
        assert response.headers["location"].rstrip("/").endswith("/events")
