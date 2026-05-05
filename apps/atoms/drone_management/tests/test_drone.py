from sqlmodel import Session
from apps.atoms.drone_management.models import Drone

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_list_drones(client, session: Session):
    drone = Drone(drone_id="D1", battery=50, status="IDLE", lat=1.1, lng=103.1)
    session.add(drone)
    session.commit()
    
    response = client.get("/drones")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["drone_id"] == "D1"

def test_get_available(client, session: Session):
    # D1 available
    session.add(Drone(drone_id="D1", battery=80, status="IDLE", lat=1.1, lng=103.1))
    # D2 low battery
    session.add(Drone(drone_id="D2", battery=20, status="IDLE", lat=1.2, lng=103.2))
    # D3 busy
    session.add(Drone(drone_id="D3", battery=80, status="IN_FLIGHT", lat=1.3, lng=103.3))
    session.commit()
    
    response = client.get("/drones/available?min_battery_pct=30")
    assert response.status_code == 200
    data = response.json()
    assert len(data["available_drones"]) == 1
    assert data["available_drones"][0]["drone_id"] == "D1"
    assert len(data["excluded_drones"]) == 2

def test_update_status(client, session: Session):
    session.add(Drone(drone_id="D1", battery=80, status="IDLE", lat=1.1, lng=103.1))
    session.commit()
    
    response = client.patch("/drones/D1/status", json={"status": "MAINTENANCE", "battery": 75})
    assert response.status_code == 200
    assert response.json()["status"] == "UPDATED"
    
    session.expire_all()
    drone = session.get(Drone, "D1")
    assert drone.status == "MAINTENANCE"
    assert drone.battery == 75

def test_update_non_existent_drone(client):
    response = client.patch("/drones/NONEXISTENT/status", json={"status": "MAINTENANCE"})
    assert response.status_code == 404
