"""
Test setup: every test gets a fresh in-memory SQLite database instead of
the real Postgres one. This keeps tests fast and deterministic and means
`pytest` works with no Docker/Postgres running at all.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_password
from app.database import Base, get_db
from app.main import app
from app.models import User

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


TEST_USERNAME = "test_hr"
TEST_PASSWORD = "test-password"


@pytest.fixture()
def client(db_session):
    """A TestClient that's already logged in as a seeded HR user, so
    every existing test can call protected endpoints without repeating
    the login dance."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    db_session.add(User(username=TEST_USERNAME, password_hash=hash_password(TEST_PASSWORD)))
    db_session.commit()

    test_client = TestClient(app)
    login_response = test_client.post(
        "/api/v1/auth/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    token = login_response.json()["access_token"]
    test_client.headers["Authorization"] = f"Bearer {token}"

    yield test_client
    app.dependency_overrides.clear()
