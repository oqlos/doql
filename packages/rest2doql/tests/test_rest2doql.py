import pytest

from rest2doql.app import create_app


def test_health() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    assert client.get("/health").json()["status"] == "ok"


def test_schema() -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    resp = client.get("/v1/schema/QUERY")
    assert resp.status_code == 200
    assert resp.json()["properties"]["verb"]["const"] == "QUERY"
