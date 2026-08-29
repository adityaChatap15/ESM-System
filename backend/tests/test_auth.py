"""Tests for login and route protection. The `client` fixture is already
logged in (see conftest.py) - these tests exercise login itself plus what
happens when a request is unauthenticated."""
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from tests.conftest import TEST_PASSWORD, TEST_USERNAME


def test_login_with_correct_credentials_returns_token(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 10


def test_login_with_wrong_password_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": TEST_USERNAME, "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_with_unknown_username_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "whatever"},
    )
    assert response.status_code == 401


def override_get_db_with(db_session):
    def override():
        yield db_session
    return override


def test_employees_endpoint_requires_auth(db_session):
    app.dependency_overrides[get_db] = override_get_db_with(db_session)
    anonymous_client = TestClient(app)  # no Authorization header set

    response = anonymous_client.get("/api/v1/employees")
    assert response.status_code == 403

    app.dependency_overrides.clear()


def test_employees_endpoint_rejects_invalid_token(db_session):
    app.dependency_overrides[get_db] = override_get_db_with(db_session)
    anonymous_client = TestClient(app)
    anonymous_client.headers["Authorization"] = "Bearer not-a-real-token"

    response = anonymous_client.get("/api/v1/employees")
    assert response.status_code == 401

    app.dependency_overrides.clear()
