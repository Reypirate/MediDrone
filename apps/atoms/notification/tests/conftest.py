import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def mock_consumer():
    with patch("apps.atoms.notification.service.run_consumer_thread"):
        yield

@pytest.fixture(name="client")
def client_fixture():
    from apps.atoms.notification.main import app
    return TestClient(app)
