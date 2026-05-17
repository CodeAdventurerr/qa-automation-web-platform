from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_generate_and_run_demo_flow():
    generated = client.post(
        "/generate-tests",
        json={"url": "https://example.com", "feature": "login form validation"},
    )

    assert generated.status_code == 200
    payload = generated.json()
    assert payload["project_id"]
    assert len(payload["test_cases"]) == 3

    run = client.post(
        "/run-tests",
        json={"project_id": payload["project_id"], "headless": True, "demo_mode": True},
    )

    assert run.status_code == 200
    report = run.json()
    assert report["total_tests"] == 3
    assert report["passed"] >= 2
    assert report["healed"] >= 1


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_key_required_when_configured(monkeypatch):
    monkeypatch.setenv("QA_PLATFORM_API_KEY", "secret")

    rejected = client.post(
        "/generate-tests",
        json={"url": "https://example.com", "feature": "login form validation"},
    )
    assert rejected.status_code == 401

    accepted = client.post(
        "/generate-tests",
        headers={"X-API-Key": "secret"},
        json={"url": "https://example.com", "feature": "login form validation"},
    )
    assert accepted.status_code == 200
