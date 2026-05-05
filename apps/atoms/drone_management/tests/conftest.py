import pytest
from fastapi.testclient import TestClient
from apps.atoms.drone_management.main import app
from shared.database import get_session
from shared.testing import db_engine, db_session

@pytest.fixture(name="session")
def session_fixture(db_session):
    yield db_session

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
