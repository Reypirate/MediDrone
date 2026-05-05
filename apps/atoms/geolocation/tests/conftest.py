import pytest
from fastapi.testclient import TestClient
from apps.atoms.geolocation.main import app

@pytest.fixture(name="client")
def client_fixture():
    return TestClient(app)
