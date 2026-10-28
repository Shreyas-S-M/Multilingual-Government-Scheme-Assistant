"""
Admin Authentication and Administrative Routes Tests.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.config import settings


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_admin_stats_unauthorized(client):
    # Without header -> 401
    res = client.get("/api/v1/admin/stats")
    assert res.status_code == 401

    # With invalid key -> 403
    res_bad = client.get("/api/v1/admin/stats", headers={"X-Admin-API-Key": "wrong-secret"})
    assert res_bad.status_code == 403


def test_admin_stats_authorized(client):
    headers = {"X-Admin-API-Key": settings.ADMIN_API_KEY}
    res = client.get("/api/v1/admin/stats", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_schemes"] >= 20
    assert "categories_breakdown" in data


def test_admin_index_rebuild(client):
    headers = {"X-Admin-API-Key": settings.ADMIN_API_KEY}
    res = client.post("/api/v1/admin/index/rebuild", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["scheme_count"] >= 20
