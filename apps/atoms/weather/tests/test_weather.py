import pytest
from unittest.mock import patch

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_weather_no_api_key(client):
    with patch("apps.atoms.weather.service.OPENWEATHER_API_KEY", ""):
        response = client.get("/weather?lat=1.3&lng=103.8")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "GOOD"
        assert data["is_flyable"] is True
        assert "condition" in data

def test_get_weather_with_api_key(client):
    # Currently the implementation is stubbed even with API key
    with patch("apps.atoms.weather.service.OPENWEATHER_API_KEY", "fake_key"):
        response = client.get("/weather?lat=1.3&lng=103.8")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "GOOD"
        assert data["is_flyable"] is True
