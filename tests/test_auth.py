"""
Unit and Integration Tests for Authentication
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from backend.database import Base, engine, SessionLocal
from backend.models import User

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    # Re-create fresh tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_register_user_success():
    payload = {
        "username": "sec_researcher",
        "email": "researcher@cyberai.local",
        "password": "StrongPassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "sec_researcher"
    assert data["user"]["email"] == "researcher@cyberai.local"
    # First user is automatically admin
    assert data["user"]["role"] == "admin"


def test_register_duplicate_username_fails():
    payload = {
        "username": "analyst1",
        "email": "analyst1@cyberai.local",
        "password": "Password123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Try duplicate username
    payload2 = {
        "username": "analyst1",
        "email": "other@cyberai.local",
        "password": "Password123"
    }
    res2 = client.post("/api/auth/register", json=payload2)
    assert res2.status_code == 400
    assert "band qilingan" in res2.json()["detail"]


def test_register_weak_password_fails():
    # Less than 8 chars
    payload = {
        "username": "user_weak",
        "email": "weak@cyberai.local",
        "password": "short"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 422  # Pydantic validation error

    # Missing digit
    payload2 = {
        "username": "user_nodigit",
        "email": "nodigit@cyberai.local",
        "password": "OnlyLettersPassword"
    }
    res2 = client.post("/api/auth/register", json=payload2)
    assert res2.status_code == 422


def test_login_success():
    # Register first
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@cyberai.local",
        "password": "TestPassword99"
    })

    # Login with username
    login_res = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "TestPassword99"
    })
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Login with email
    login_email_res = client.post("/api/auth/login", json={
        "username": "test@cyberai.local",
        "password": "TestPassword99"
    })
    assert login_email_res.status_code == 200


def test_login_invalid_password_fails():
    client.post("/api/auth/register", json={
        "username": "victim",
        "email": "victim@cyberai.local",
        "password": "CorrectPassword123"
    })

    res = client.post("/api/auth/login", json={
        "username": "victim",
        "password": "WrongPassword999"
    })
    assert res.status_code == 401
    assert "noto'g'ri" in res.json()["detail"]


def test_get_me_protected_route():
    # Without token
    res_no_auth = client.get("/api/auth/me")
    assert res_no_auth.status_code == 401

    # Register and get token
    reg = client.post("/api/auth/register", json={
        "username": "profileuser",
        "email": "profile@cyberai.local",
        "password": "ProfilePassword1"
    }).json()

    token = reg["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res_auth = client.get("/api/auth/me", headers=headers)
    assert res_auth.status_code == 200
    assert res_auth.json()["username"] == "profileuser"
