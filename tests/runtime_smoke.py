"""End-to-end runtime smoke test for the generated asset-management API.

Assumes the API is running at http://127.0.0.1:8765.
Run manually with:
    /tmp/doql-runtime/bin/python tests/runtime_smoke.py
"""
from __future__ import annotations

import sys

import httpx


BASE = "http://127.0.0.1:8766"


def step(client: httpx.Client, name: str, response: httpx.Response, expected: int | None = None) -> httpx.Response:
    ok = (expected is None and 200 <= response.status_code < 300) or response.status_code == expected
    icon = "✓" if ok else "✗"
    print(f"  {icon} [{response.status_code}] {name}")
    if not ok:
        print(f"    body: {response.text[:300]}")
        sys.exit(1)
    return response


def main() -> int:
    with httpx.Client(base_url=BASE, timeout=5.0) as c:
        print("=== 1. Health ===")
        r = step(c, "GET /health", c.get("/health"))
        assert r.json()["status"] == "ok"

        print("\n=== 2. Auth flow (JWT + RBAC) ===")
        step(c, "register alice (admin)", c.post("/auth/register",
            json={"username": "alice", "password": "secret123", "role": "admin"}), 201)
        r = step(c, "login alice", c.post("/auth/login",
            data={"username": "alice", "password": "secret123"}))
        token = r.json()["access_token"]
        auth = {"Authorization": f"Bearer {token}"}
        me = step(c, "/auth/me with token", c.get("/auth/me", headers=auth)).json()
        assert me["username"] == "alice", me
        assert me["role"] == "admin", me

        r = c.get("/auth/me")
        assert r.status_code == 401
        print(f"  ✓ [{r.status_code}] unauth /auth/me → 401")

        print("\n=== 3. CRUD Station (entity with explicit id) ===")
        r = step(c, "POST /stations", c.post("/api/v1/stations",
            json={"name": "Warsaw-1", "address": "Main 1", "manager": "Bob"}), 201)
        sid = r.json()["id"]
        step(c, "GET /stations list", c.get("/api/v1/stations"))
        step(c, "GET /stations/{id}", c.get(f"/api/v1/stations/{sid}"))
        r = step(c, "PATCH /stations/{id}", c.patch(f"/api/v1/stations/{sid}",
            json={"address": "Updated"}))
        assert r.json()["address"] == "Updated"
        step(c, "DELETE /stations/{id}", c.delete(f"/api/v1/stations/{sid}"), 204)

        print("\n=== 4. CRUD Qualification (no id field — auto-PK) ===")
        r = step(c, "POST /qualifications", c.post("/api/v1/qualifications",
            json={"name": "SCBA-Advanced", "level": "advanced"}), 201)
        qid = r.json()["id"]
        assert qid, "auto-PK id must be present in response"
        print(f"    auto-PK: {qid}")
        step(c, "DELETE /qualifications/{id}", c.delete(f"/api/v1/qualifications/{qid}"), 204)

        print("\n=== 5. Device with ForeignKey → Station ===")
        r = c.post("/api/v1/stations", json={"name": "Krakow-1"})
        station_id = r.json()["id"]
        r = step(c, "POST /devices (station FK)", c.post("/api/v1/devices",
            json={"serial": "SN-001", "model": "X100", "manufacturer": "ACME",
                  "device_type": "scba", "station": station_id, "status": "ready"}), 201)
        did = r.json()["id"]
        dev = step(c, "GET /devices/{id}", c.get(f"/api/v1/devices/{did}")).json()
        assert dev["station"] == station_id

        print("\n=== 6. OpenAPI schema ===")
        schema = c.get("/openapi.json").json()
        paths = sorted(schema["paths"].keys())
        print(f"  ✓ {len(paths)} endpoints exposed")
        print(f"  ✓ title: {schema['info']['title']} v{schema['info']['version']}")
        # Spot-check auth endpoints are in there
        for expected in ("/auth/register", "/auth/login", "/auth/me", "/api/v1/stations"):
            assert expected in schema["paths"], f"missing path: {expected}"

        print("\n🎉 ALL RUNTIME SMOKE TESTS PASSED 🎉")
        return 0


if __name__ == "__main__":
    sys.exit(main())
