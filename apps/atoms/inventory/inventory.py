import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from shared.database import get_session, init_db
from shared.tracking import RequestTrackingMiddleware
from sqlmodel import Field, Session, SQLModel, func, select


# Models
class Inventory(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    hospital_id: str = Field(primary_key=True)
    item_id: str = Field(primary_key=True)
    name: str
    quantity: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Inventory Service", lifespan=lifespan)
app.add_middleware(RequestTrackingMiddleware)


@app.post("/inventory/reserve")
async def reserve(data: dict, session: Session = Depends(get_session)):
    order_id = data.get("order_id")
    hospital_id = data.get("hospital_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)

    if not hospital_id:
        raise HTTPException(
            status_code=400,
            detail={"status": "FAILED", "reason": "HOSPITAL_ID_REQUIRED", "order_id": order_id},
        )

    # In SQLModel, manual 'FOR UPDATE' requires raw SQL or specific extensions.
    # For now, we'll do a simple select.
    item = session.get(Inventory, (hospital_id, item_id))
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"status": "FAILED", "reason": "ITEM_NOT_FOUND", "order_id": order_id},
        )

    if item.quantity < quantity:
        raise HTTPException(
            status_code=409,
            detail={
                "status": "FAILED",
                "reason": "INSUFFICIENT_STOCK",
                "order_id": order_id,
                "hospital_id": hospital_id,
                "available": item.quantity,
                "requested": quantity,
            },
        )

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


@app.post("/inventory/release")
async def release(data: dict, session: Session = Depends(get_session)):
    order_id = data.get("order_id")
    hospital_id = data.get("hospital_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 0)

    if not quantity and "items" in data:
        items = data["items"]
        if items:
            item_id = items[0].get("item_id")
            quantity = items[0].get("reserved_quantity", 0)

    if not hospital_id:
        raise HTTPException(
            status_code=400,
            detail={"status": "FAILED", "reason": "HOSPITAL_ID_REQUIRED", "order_id": order_id},
        )

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


@app.get("/inventory")
def list_inventory(hospital_id: str = None, session: Session = Depends(get_session)):
    statement = select(Inventory)
    if hospital_id:
        statement = statement.where(Inventory.hospital_id == hospital_id)
    return session.exec(statement.order_by(Inventory.hospital_id, Inventory.item_id)).all()


@app.get("/inventory/items")
def list_items(session: Session = Depends(get_session)):
    statement = select(
        Inventory.item_id, Inventory.name, func.sum(Inventory.quantity).label("total_quantity")
    ).group_by(Inventory.item_id, Inventory.name)
    results = session.exec(statement).all()
    return [{"item_id": r[0], "name": r[1], "total_quantity": r[2]} for r in results]


@app.get("/inventory/search")
def search(item_id: str, quantity: int = 1, session: Session = Depends(get_session)):
    statement = (
        select(Inventory)
        .where(Inventory.item_id == item_id)
        .where(Inventory.quantity >= quantity)
        .order_by(Inventory.quantity.desc())
    )
    rows = session.exec(statement).all()
    return {
        "item_id": item_id,
        "requested_quantity": quantity,
        "hospitals": [{"hospital_id": r.hospital_id, "available": r.quantity} for r in rows],
    }


@app.post("/inventory/restock")
async def restock(session: Session = Depends(get_session)):
    seed_data = [
        ("HOSP-001", "BLOOD-O-NEG", "O-Negative Blood Bags", 50),
        ("HOSP-001", "BLOOD-A-POS", "A-Positive Blood Bags", 30),
        ("HOSP-001", "BLOOD-B-POS", "B-Positive Blood Bags", 15),
        ("HOSP-002", "BLOOD-O-NEG", "O-Negative Blood Bags", 20),
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


@app.get("/health")
def health(session: Session = Depends(get_session)):
    try:
        count = session.exec(select(func.count()).select_from(Inventory)).one()
        return {"status": "healthy", "service": "inventory", "inventory_count": count}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 4004))
    uvicorn.run(app, host="0.0.0.0", port=port)
