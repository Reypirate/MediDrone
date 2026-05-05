from apps.composites.drone_dispatch.models import Mission

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_start_mission(client, session):
    payload = {
        "order_id": "O1",
        "drone_id": "D1",
        "start_lat": 1.3,
        "start_lng": 103.8,
        "target_lat": 1.4,
        "target_lng": 103.9
    }
    
    response = client.post("/dispatch/missions", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
    assert response.json()["mission"]["order_id"] == "O1"
    
    # Verify DB entry
    mission = session.get(Mission, "O1")
    assert mission is not None
    assert mission.drone_id == "D1"

def test_get_mission(client, session):
    mission = Mission(order_id="O2", drone_id="D2", current_lat=1.0, current_lng=1.0, target_lat=1.1, target_lng=1.1, eta_minutes=10.0)
    session.add(mission)
    session.commit()
    
    response = client.get("/dispatch/missions/O2")
    assert response.status_code == 200
    assert response.json()["drone_id"] == "D2"

def test_get_mission_not_found(client):
    response = client.get("/dispatch/missions/NONEXISTENT")
    assert response.status_code == 404
