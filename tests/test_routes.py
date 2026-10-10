"""Route-level contract tests for GET /events and POST /risk/score."""

from fastapi.testclient import TestClient

from app import stellar
from app.config import Settings
from app.main import app

client = TestClient(app)
ADDRESS = "G" + "A" * 55
CONTRACT_ID = "C" + "A" * 55


def _stub_events(monkeypatch, contract_id=CONTRACT_ID):
    monkeypatch.setattr(stellar, "get_settings", lambda: Settings(contract_id=contract_id))

    def fake_rpc(method, params, settings):
        if method == "getHealth":
            return {"latestLedger": 100000, "oldestLedger": 80000}
        return {
            "events": [
                {
                    "id": "id1",
                    "ledger": 99999,
                    "ledgerClosedAt": "now",
                    "contractId": contract_id,
                    "topic": [
                        {"symbol": "flagged"},
                        {"address": {"accountId": "agent"}},
                        {"address": {"accountId": "subject"}},
                    ],
                    "value": {"u32": 82},
                }
            ],
            "cursor": "opaque",
        }

    monkeypatch.setattr(stellar, "_rpc", fake_rpc)


def test_events_limit_query_bounds(monkeypatch):
    _stub_events(monkeypatch)
    assert client.get("/events?limit=0").status_code == 422
    assert client.get("/events?limit=101").status_code == 422
    assert client.get("/events?limit=1").status_code == 200
    assert client.get("/events?limit=100").status_code == 200


def test_events_cursor_query_bounds(monkeypatch):
    _stub_events(monkeypatch)
    assert client.get("/events?cursor=").status_code == 422


def test_risk_score_rejects_invalid_addresses():
    assert client.post("/risk/score", json={"address": ADDRESS.lower()}).status_code == 422
    assert client.post("/risk/score", json={"address": "G" + "A" * 53}).status_code == 422


def test_events_success_returns_decoded_shape(monkeypatch):
    _stub_events(monkeypatch)
    response = client.get("/events")
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) >= {"events", "next_cursor", "source"}
    assert payload["events"][0]["agent"] == "agent"
    assert payload["events"][0]["subject"] == "subject"
    assert payload["next_cursor"] == "opaque"


def test_events_without_contract_id_returns_503(monkeypatch):
    _stub_events(monkeypatch, contract_id="")
    response = client.get("/events")
    assert response.status_code == 503
