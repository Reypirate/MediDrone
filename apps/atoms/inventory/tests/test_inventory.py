from sqlmodel import Session, select
from apps.atoms.inventory.models import Inventory

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_search_inventory(client, session: Session):
    session.add(Inventory(hospital_id="H1", item_id="I1", name="Bandages", quantity=100))
    session.add(Inventory(hospital_id="H2", item_id="I1", name="Bandages", quantity=50))
    session.commit()
    
    response = client.get("/inventory/search?item_id=I1&quantity=60")
    assert response.status_code == 200
    data = response.json()
    assert len(data["hospitals"]) == 1
    assert data["hospitals"][0]["hospital_id"] == "H1"

def test_reserve_inventory(client, session: Session):
    session.add(Inventory(hospital_id="H1", item_id="I1", name="Bandages", quantity=100))
    session.commit()
    
    response = client.post("/inventory/reserve", json={"hospital_id": "H1", "item_id": "I1", "quantity": 10})
    assert response.status_code == 200
    assert response.json()["status"] == "RESERVED"
    
    session.expire_all()
    item = session.get(Inventory, ("H1", "I1"))
    assert item.quantity == 90

def test_reserve_insufficient_stock(client, session: Session):
    session.add(Inventory(hospital_id="H1", item_id="I1", name="Bandages", quantity=5))
    session.commit()
    
    response = client.post("/inventory/reserve", json={"hospital_id": "H1", "item_id": "I1", "quantity": 10})
    assert response.status_code == 409 
    assert response.json()["detail"]["reason"] == "INSUFFICIENT_STOCK"

def test_release_inventory(client, session: Session):
    session.add(Inventory(hospital_id="H1", item_id="I1", name="Bandages", quantity=90))
    session.commit()
    
    # Original release expected direct hospital_id and item_id in body
    response = client.post("/inventory/release", json={"hospital_id": "H1", "item_id": "I1", "quantity": 10})
    assert response.status_code == 200
    assert response.json()["status"] == "RELEASED"
    
    session.expire_all()
    item = session.get(Inventory, ("H1", "I1"))
    assert item.quantity == 100

def test_restock(client):
    response = client.post("/inventory/restock")
    assert response.status_code == 200
    assert response.json()["status"] == "RESTOCKED"

def test_list_items(client, session: Session):
    session.add(Inventory(hospital_id="H1", item_id="I1", name="Bandages", quantity=100))
    session.add(Inventory(hospital_id="H2", item_id="I1", name="Bandages", quantity=50))
    session.commit()
    
    response = client.get("/inventory/items")
    assert response.status_code == 200
    data = response.json()
    assert data[0]["item_id"] == "I1"
    assert data[0]["total_quantity"] == 150

def test_list_all_inventory(client, session: Session):
    session.add(Inventory(hospital_id="H1", item_id="I1", name="Bandages", quantity=100))
    session.commit()
    
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.json()) >= 1
