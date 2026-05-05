from sqlmodel import Session, select, func
from fastapi import HTTPException
from .models import Inventory

def reserve_inventory(session: Session, data: dict):
    hospital_id = data.get("hospital_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)
    order_id = data.get("order_id")

    if not hospital_id:
        raise HTTPException(status_code=400, detail="HOSPITAL_ID_REQUIRED")

    item = session.get(Inventory, (hospital_id, item_id))
    if not item:
        raise HTTPException(status_code=404, detail="ITEM_NOT_FOUND")

    if item.quantity < quantity:
        return {
            "status": "FAILED",
            "reason": "INSUFFICIENT_STOCK",
            "order_id": order_id,
            "hospital_id": hospital_id,
            "available": item.quantity,
            "requested": quantity,
        }

    item.quantity -= quantity
    session.add(item)
    session.commit()
    session.refresh(item)

    return {
        "status": "RESERVED",
        "order_id": order_id,
        "hospital_id": hospital_id,
        "item_id": item_id,
        "reserved_quantity": quantity,
        "remaining_stock": item.quantity,
    }

def release_inventory(session: Session, data: dict):
    hospital_id = data.get("hospital_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 0)
    order_id = data.get("order_id")

    item = session.get(Inventory, (hospital_id, item_id))
    if item:
        item.quantity += quantity
        session.add(item)
        session.commit()

    return {
        "status": "RELEASED",
        "order_id": order_id,
        "hospital_id": hospital_id,
        "item_id": item_id,
        "released_quantity": quantity,
    }

def get_inventory(session: Session, hospital_id: str = None):
    query = select(Inventory)
    if hospital_id:
        query = query.where(Inventory.hospital_id == hospital_id)
    return session.exec(query.order_by(Inventory.hospital_id, Inventory.item_id)).all()

def get_distinct_items(session: Session):
    results = session.exec(select(Inventory.item_id, Inventory.name, func.sum(Inventory.quantity)).group_by(Inventory.item_id, Inventory.name)).all()
    return [{"item_id": r[0], "name": r[1], "total_quantity": r[2]} for r in results]

def search_inventory(session: Session, item_id: str, quantity: int = 1):
    query = select(Inventory).where(Inventory.item_id == item_id, Inventory.quantity >= quantity).order_by(Inventory.quantity.desc())
    rows = session.exec(query).all()
    return {
        "item_id": item_id,
        "requested_quantity": quantity,
        "hospitals": [{"hospital_id": r.hospital_id, "available": r.quantity} for r in rows],
    }

def restock_inventory(session: Session):
    seed_data = [
        ("HOSP-001", "BLOOD-O-NEG", "O-Negative Blood Bags", 50),
        ("HOSP-001", "BLOOD-A-POS", "A-Positive Blood Bags", 30),
        ("HOSP-001", "BLOOD-B-POS", "B-Positive Blood Bags", 15),
        ("HOSP-001", "DEFIB-01", "Portable Defibrillator", 8),
        ("HOSP-001", "ORGAN-KIT-01", "Organ Transport Kit", 5),
        ("HOSP-001", "EPINEPHRINE-01", "Epinephrine Auto-Injector", 20),
        ("HOSP-002", "BLOOD-O-NEG", "O-Negative Blood Bags", 20),
        ("HOSP-002", "BLOOD-B-POS", "B-Positive Blood Bags", 25),
        ("HOSP-003", "BLOOD-O-NEG", "O-Negative Blood Bags", 35),
    ]
    for h_id, i_id, name, qty in seed_data:
        item = session.get(Inventory, (h_id, i_id))
        if item:
            item.quantity = qty
        else:
            item = Inventory(hospital_id=h_id, item_id=i_id, name=name, quantity=qty)
        session.add(item)
    session.commit()
    return {"status": "RESTOCKED", "items_reset": len(seed_data)}

def get_health(session: Session):
    try:
        count = session.exec(select(func.count(Inventory.item_id))).one()
        return {"status": "healthy", "service": "inventory", "inventory_count": count}
    except Exception as e:
        return {"status": "unhealthy", "service": "inventory", "error": str(e)}
