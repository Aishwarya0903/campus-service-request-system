import os

os.environ["JWT_SECRET"] = "test-secret-for-pytest-only"

from fastapi.testclient import TestClient
from app.main import app, classify

client = TestClient(app)


def test_student_login_succeeds():
    response = client.post(
        "/auth/login",
        json={
            "email": "22MIS0281",
            "password": "winter@123",
            "portal": "student"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["role"] == "STUDENT"
    assert data["name"] == "Aishwarya Student"


def test_student_credentials_are_rejected_from_staff_portal():
    response = client.post(
        "/auth/login",
        json={
            "email": "22MIS0281",
            "password": "winter@123",
            "portal": "staff"
        }
    )

    assert response.status_code == 403

    assert (
        response.json()["detail"]
        == "These credentials are not valid for the selected portal"
    )


def test_invalid_password_is_rejected():
    response = client.post(
        "/auth/login",
        json={
            "email": "22MIS0281",
            "password": "wrong-password",
            "portal": "student"
        }
    )

    assert response.status_code == 401


def test_ai_classification_returns_category_and_priority():
    category, priority = classify(
        "The Wi-Fi connection in my hostel room is not working."
    )

    assert isinstance(category, str)
    assert isinstance(priority, str)

    assert category.strip() != ""
    assert priority.strip() != ""


def test_ai_classification_produces_valid_priority():
    category, priority = classify(
        "There is an urgent network problem and I cannot connect to the campus Wi-Fi."
    )

    assert priority in {
        "LOW",
        "MEDIUM",
        "HIGH"
    }


def test_required_core_api_endpoints_are_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/auth/login" in paths
    assert "/tickets" in paths
    assert "/notifications" in paths
    assert "/sla/rules" in paths
    assert "/analytics/overview" in paths
