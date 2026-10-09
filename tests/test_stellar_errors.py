"""Tests for app.stellar HTTP error mapping and ScVal decode helpers."""

import base64

import httpx
import pytest
from fastapi import HTTPException

from app import stellar
from app.config import Settings

SETTINGS = Settings()


def _status_error(status_code: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://example.invalid")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError("%d response" % status_code, request=request, response=response)


def test_get_maps_missing_account_to_404(monkeypatch):
    def raise_404(*args, **kwargs):
        raise _status_error(404)

    monkeypatch.setattr(httpx, "get", raise_404)
    with pytest.raises(HTTPException) as excinfo:
        stellar._get("https://example.invalid/accounts/missing", settings=SETTINGS)
    assert excinfo.value.status_code == 404


def test_get_maps_non_404_status_to_502(monkeypatch):
    def raise_500(*args, **kwargs):
        raise _status_error(500)

    monkeypatch.setattr(httpx, "get", raise_500)
    with pytest.raises(HTTPException) as excinfo:
        stellar._get("https://example.invalid/accounts/broken", settings=SETTINGS)
    assert excinfo.value.status_code == 502


def test_get_maps_transport_error_to_503(monkeypatch):
    def raise_connect(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "get", raise_connect)
    with pytest.raises(HTTPException) as excinfo:
        stellar._get("https://example.invalid/accounts/unreachable", settings=SETTINGS)
    assert excinfo.value.status_code == 503


def test_rpc_maps_http_status_error_to_502(monkeypatch):
    def raise_500(*args, **kwargs):
        raise _status_error(500)

    monkeypatch.setattr(httpx, "post", raise_500)
    with pytest.raises(HTTPException) as excinfo:
        stellar._rpc("getHealth", {}, settings=SETTINGS)
    assert excinfo.value.status_code == 502


def test_rpc_maps_jsonrpc_error_body_to_502(monkeypatch):
    def fake_post(url, **kwargs):
        return httpx.Response(200, json={"error": {"code": -32000}}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    with pytest.raises(HTTPException) as excinfo:
        stellar._rpc("getEvents", {}, settings=SETTINGS)
    assert excinfo.value.status_code == 502


def test_rpc_maps_transport_error_to_503(monkeypatch):
    def raise_connect(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", raise_connect)
    with pytest.raises(HTTPException) as excinfo:
        stellar._rpc("getHealth", {}, settings=SETTINGS)
    assert excinfo.value.status_code == 503


def test_symbol_scval_encodes_scv_symbol():
    raw = base64.b64decode(stellar._symbol_scval("flagged"))
    assert int.from_bytes(raw[:4], "big") == 15  # SCV_SYMBOL
    length = int.from_bytes(raw[4:8], "big")
    assert length == len(b"flagged")
    assert raw[8:8 + length] == b"flagged"


def test_native_decodes_scalar_address_and_vec():
    assert stellar._native({"u32": 82}) == 82
    assert stellar._native({"address": {"accountId": "GACCOUNT"}}) == "GACCOUNT"
    assert stellar._native({"address": {"contractId": "CCONTRACT"}}) == "CCONTRACT"
    assert stellar._native({"vec": [{"u32": 1}, {"u32": 2}]}) == [1, 2]
