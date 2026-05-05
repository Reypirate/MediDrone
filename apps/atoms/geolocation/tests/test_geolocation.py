import pytest
import respx
from httpx import Response
from unittest.mock import patch

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_geocode_fallback(client):
    with patch("apps.atoms.geolocation.service.GOOGLE_MAPS_API_KEY", ""):
        with patch("apps.atoms.geolocation.service.geocode_cache", {}):
            response = client.get("/maps/api/geocode/json?address=Changi Airport")
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "FALLBACK"

@respx.mock
def test_geocode_external(client):
    mock_response = {
        "status": "OK",
        "results": [{
            "geometry": {"location": {"lat": 1.3521, "lng": 103.8198}},
            "formatted_address": "Mock Address, Singapore"
        }]
    }
    
    respx.get("https://maps.googleapis.com/maps/api/geocode/json").mock(return_value=Response(200, json=mock_response))
    
    with patch("apps.atoms.geolocation.service.GOOGLE_MAPS_API_KEY", "fake_key"):
        with patch("apps.atoms.geolocation.service.geocode_cache", {}):
            response = client.get("/maps/api/geocode/json?address=Test Address")
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "EXTERNAL_API"
            assert data["customer_coords"]["lat"] == 1.3521
            assert data["region_valid"] is True

@respx.mock
def test_geocode_invalid_region(client):
    mock_response = {
        "status": "OK",
        "results": [{
            "geometry": {"location": {"lat": 40.7128, "lng": -74.0060}}, # New York
            "formatted_address": "NYC, USA"
        }]
    }
    
    respx.get("https://maps.googleapis.com/maps/api/geocode/json").mock(return_value=Response(200, json=mock_response))
    
    with patch("apps.atoms.geolocation.service.GOOGLE_MAPS_API_KEY", "fake_key"):
        with patch("apps.atoms.geolocation.service.geocode_cache", {}):
            response = client.get("/maps/api/geocode/json?address=NYC")
            assert response.status_code == 200
            assert response.json()["region_valid"] is False
