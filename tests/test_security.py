"""
Unit and Integration Tests for Defensive Security Tools
Covers Code Security Analyzer and Website Security Checker (including SSRF defense).
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from backend.database import Base, engine
from backend.security_analyzer import analyze_code_security
from backend.website_checker import validate_and_resolve_url, SSRFValidationError

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def get_auth_token():
    res = client.post("/api/auth/register", json={
        "username": "sec_auditor",
        "email": "auditor@cyberai.local",
        "password": "AuditorPassword123"
    })
    return res.json()["access_token"]


# ==========================================
# Code Analyzer Tests
# ==========================================

def test_analyzer_detects_hardcoded_aws_key():
    vuln_code = 'AWS_KEY = "AKIA1234567890EXAMPLE"\nprint(AWS_KEY)'
    result = analyze_code_security(vuln_code, language="python")
    assert result["score"] < 100
    findings = result["findings"]
    assert any(f["name"] == "AWS Access Key ID" for f in findings)


def test_analyzer_detects_sql_injection():
    vuln_code = """
def get_user(cursor, uid):
    query = f"SELECT * FROM users WHERE id = '{uid}'"
    return cursor.execute(query)
"""
    result = analyze_code_security(vuln_code, language="python")
    assert result["score"] <= 75
    findings = result["findings"]
    assert any("SQL" in f["category"] for f in findings)
    assert any(f["line"] == 3 for f in findings)


def test_analyzer_detects_dangerous_eval():
    vuln_code = "result = eval(user_input)"
    result = analyze_code_security(vuln_code, language="python")
    assert result["score"] <= 75
    findings = result["findings"]
    assert any("eval" in f["name"].lower() for f in findings)


def test_analyzer_detects_js_innerhtml_and_eval():
    vuln_js = """
function render() {
    eval("alert('test')");
    document.getElementById("output").innerHTML = userInput;
}
"""
    result = analyze_code_security(vuln_js, language="javascript")
    assert result["score"] <= 80
    assert len(result["findings"]) >= 2


def test_analyzer_clean_code_scores_100():
    safe_code = """
import os

def calculate_sum(a: int, b: int) -> int:
    return a + b
"""
    result = analyze_code_security(safe_code, language="python")
    assert result["score"] == 100
    assert result["risk_level"] == "SECURE"
    assert len(result["findings"]) == 0


def test_code_analysis_api_endpoint():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "code": "cursor.execute(f'SELECT * FROM items WHERE id = {val}')",
        "language": "python"
    }
    res = client.post("/api/security/analyze-code", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "risk_level" in data
    assert data["findings_count"] > 0


# ==========================================
# Website Checker & SSRF Prevention Tests
# ==========================================

def test_ssrf_rejects_localhost():
    with pytest.raises(SSRFValidationError):
        validate_and_resolve_url("http://localhost:8000")

    with pytest.raises(SSRFValidationError):
        validate_and_resolve_url("http://127.0.0.1:8000")


def test_ssrf_rejects_private_network():
    # 10.0.0.1
    with pytest.raises(SSRFValidationError):
        validate_and_resolve_url("http://10.0.0.1")

    # 192.168.1.1
    with pytest.raises(SSRFValidationError):
        validate_and_resolve_url("http://192.168.1.1")


def test_ssrf_rejects_cloud_metadata():
    with pytest.raises(SSRFValidationError):
        validate_and_resolve_url("http://169.254.169.254/latest/meta-data/")


def test_website_checker_endpoint_blocks_ssrf():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "url": "http://127.0.0.1:8000/internal-admin",
        "confirm_authorization": True
    }
    res = client.post("/api/security/check-website", json=payload, headers=headers)
    assert res.status_code == 400
    assert "SSRF" in res.json()["detail"]


def test_website_checker_requires_authorization_confirmation():
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "url": "https://example.com",
        "confirm_authorization": False
    }
    res = client.post("/api/security/check-website", json=payload, headers=headers)
    assert res.status_code == 422 or res.status_code == 400
