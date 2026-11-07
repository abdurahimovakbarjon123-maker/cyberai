"""
Unit and Integration Tests for Administrator Dashboard & System Health
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from backend.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app"] == "CYBERAI"


def test_admin_access_control():
    # First user registered is admin
    admin_reg = client.post("/api/auth/register", json={
        "username": "superadmin",
        "email": "admin@cyberai.local",
        "password": "AdminPassword123"
    }).json()
    admin_token = admin_reg["access_token"]
    assert admin_reg["user"]["role"] == "admin"

    # Second user registered is regular user
    user_reg = client.post("/api/auth/register", json={
        "username": "normaluser",
        "email": "user@cyberai.local",
        "password": "UserPassword123"
    }).json()
    user_token = user_reg["access_token"]
    assert user_reg["user"]["role"] == "user"

    # Regular user attempting to access admin stats -> 403 Forbidden
    res_forbidden = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {user_token}"})
    assert res_forbidden.status_code == 403

    # Admin user accessing admin stats -> 200 OK
    res_admin = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    stats = res_admin.json()
    assert stats["total_users"] == 2
    assert "system_health" in stats

    # Admin accessing user list
    res_users = client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_users.status_code == 200
    users = res_users.json()
    assert len(users) == 2

    # Admin accessing audit logs
    res_logs = client.get("/api/admin/logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_logs.status_code == 200

    # Admin accessing system diagnostics
    res_sys = client.get("/api/admin/system", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_sys.status_code == 200
    assert res_sys.json()["status"] == "healthy"
