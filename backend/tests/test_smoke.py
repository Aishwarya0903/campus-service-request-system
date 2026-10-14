import os

os.environ["JWT_SECRET"] = "test-secret-for-pytest-only"

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_application_starts():
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "paths" in data


def test_unauthenticated_ticket_request_is_rejected():
    response = client.get("/tickets")
    assert response.status_code in (401, 403)


def test_unauthenticated_notifications_request_is_rejected():
    response = client.get("/notifications")
    assert response.status_code in (401, 403)


def test_unauthenticated_sla_rules_are_rejected():
    response = client.get("/sla/rules")
    assert response.status_code in (401, 403)