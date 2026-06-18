import os

os.environ["MOCK_LLM"] = "true"  # run without Ollama

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_p1_goes_through_remediation():
    payload = {
        "id": "INC-TEST-1",
        "title": "Checkout API outage - all users affected",
        "description": "500 errors at 100% on /checkout. Service is down after the latest deploy.",
    }
    r = client.post("/process", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["severity"] == "P1"
    assert body["path"] == "auto_remediation"
    # remediation should have invoked at least one tool (page_oncall + a safe action)
    assert body["remediation"] is not None
    assert len(body["remediation"]["tools_invoked"]) >= 1


def test_p4_skips_remediation():
    payload = {
        "title": "Informational: maintenance window reminder",
        "description": "Notice only, no action needed.",
    }
    r = client.post("/process", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["severity"] == "P4"
    assert body["path"] == "notify_only"
    assert body["remediation"] is None


def test_lookup_past_incident():
    r = client.get("/incidents/INC-101")
    assert r.status_code == 200
    assert r.json()["category"] == "application"


def test_process_requires_title():
    r = client.post("/process", json={"title": "  "})
    assert r.status_code == 400
