def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_plan_route(client):
    params = {
        "start_lat": 1.3521,
        "start_lng": 103.8198,
        "end_lat": 1.3644,
        "end_lng": 103.9915
    }
    response = client.get("/route/plan", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "distance_km" in data
    assert "waypoints" in data
    assert data["distance_km"] > 0
    assert len(data["waypoints"]) >= 2

def test_plan_route_missing_data(client):
    response = client.get("/route/plan", params={"start_lat": 1.2})
    assert response.status_code == 422 # FastAPI validation error
