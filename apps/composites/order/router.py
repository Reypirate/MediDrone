import uuid
import requests as http_requests
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from shared.database import get_session
from . import service
from .models import Order

router = APIRouter()


@router.post("/order", status_code=201)
def create_order(data: dict, session: Session = Depends(get_session)):
    hospital_id = data.get("hospital_id")
    item_id = data.get("item_id")
    quantity = data.get("quantity", 1)
    urgency_level = data.get("urgency_level", "NORMAL")
    customer_address = data.get("customer_address", "")
    customer_coords = data.get("customer_coords")

    if not customer_coords or "lat" not in customer_coords:
        raise HTTPException(status_code=400, detail="CUSTOMER_COORDS_REQUIRED")
    if not item_id:
        raise HTTPException(status_code=400, detail="ITEM_ID_REQUIRED")

    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    distance_km = None
    hospital_name = None

    if hospital_id:
        try:
            resp = http_requests.get(f"{service.HOSPITAL_URL}/hospitals/{hospital_id}", timeout=10)
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="INVALID_HOSPITAL")
            hosp_data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=str(e))

        hospital_name = hosp_data.get("name", hospital_id)
        distance_km = service.haversine(
            customer_coords["lat"], customer_coords["lng"], hosp_data["lat"], hosp_data["lng"]
        )
    else:
        nearest, error = service.find_nearest_hospital(customer_coords, item_id, quantity)
        if not nearest:
            service.create_order_record(
                session,
                {
                    "order_id": order_id,
                    "item_id": item_id,
                    "quantity": quantity,
                    "urgency_level": urgency_level,
                    "customer_address": customer_address,
                    "customer_lat": customer_coords["lat"],
                    "customer_lng": customer_coords["lng"],
                    "status": f"FAILED_{error}",
                },
            )
            service.publish_message(
                "notifications",
                "notify.sms",
                {"event_type": "ORDER_FAILED", "order_id": order_id, "message": f"Order {order_id} failed: {error}."},
            )
            raise HTTPException(status_code=409, detail=error)

        hospital_id = nearest["hospital_id"]
        hospital_name = nearest["name"]
        distance_km = nearest["distance_km"]

    new_order = service.create_order_record(
        session,
        {
            "order_id": order_id,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "item_id": item_id,
            "quantity": quantity,
            "urgency_level": urgency_level,
            "customer_address": customer_address,
            "customer_lat": customer_coords["lat"],
            "customer_lng": customer_coords["lng"],
            "status": "PENDING",
        },
    )

    # Reserve inventory
    try:
        reserve_resp = http_requests.post(
            f"{service.INVENTORY_URL}/inventory/reserve",
            json={"order_id": order_id, "hospital_id": hospital_id, "item_id": item_id, "quantity": quantity},
            timeout=10,
        )
        reserve_data = reserve_resp.json()
    except Exception as e:
        service.update_order_status(session, order_id, {"status": "ERROR"})
        raise HTTPException(status_code=503, detail=str(e))

    if reserve_data.get("status") != "RESERVED":
        service.update_order_status(session, order_id, {"status": "FAILED_STOCK"})
        service.publish_message("orders", "order.failed", {"order_id": order_id})
        service.publish_message(
            "notifications",
            "notify.sms",
            {"order_id": order_id, "event_type": "ORDER_FAILED", "message": "Insufficient stock"},
        )
        raise HTTPException(status_code=409, detail=reserve_data.get("reason", "INSUFFICIENT_STOCK"))

    service.update_order_status(session, order_id, {"status": "CONFIRMED"})

    payload = {
        "order_id": order_id,
        "hospital_id": hospital_id,
        "item_id": item_id,
        "quantity": quantity,
        "urgency_level": urgency_level,
        "customer_address": customer_address,
        "customer_coords": customer_coords,
    }
    service.publish_message("orders", "order.confirmed", payload)
    service.publish_message(
        "notifications",
        "notify.sms",
        {"order_id": order_id, "event_type": "ORDER_CONFIRMED", "message": f"Order {order_id} confirmed."},
    )

    return {
        "order_id": order_id,
        "status": "CONFIRMED",
        "hospital_id": hospital_id,
        "hospital_name": hospital_name,
        "distance_km": round(distance_km, 2) if distance_km else None,
    }


@router.get("/orders")
def list_orders(status: str | None = None, session: Session = Depends(get_session)):
    results = service.get_orders(session, status)
    return {"orders": results}


@router.get("/order/{order_id}")
def get_order(order_id: str, session: Session = Depends(get_session)):
    order = service.get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/dispatch/confirm")
def dispatch_confirm(data: dict, session: Session = Depends(get_session)):
    updates = {
        "status": data.get("status", "TO_HOSPITAL"),
        "drone_id": data.get("drone_id"),
        "eta_minutes": data.get("eta_minutes"),
    }
    order = service.update_order_status(session, data.get("order_id"), updates)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status": "SUCCESS", "order_id": order.order_id}


@router.post("/dispatch/update")
def dispatch_update(data: dict, session: Session = Depends(get_session)):
    order = service.update_order_status(session, data.get("order_id"), data)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status": "SUCCESS", "order_id": order.order_id}


@router.post("/dispatch/complete")
def dispatch_complete(data: dict, session: Session = Depends(get_session)):
    order_id = data.get("order_id")
    updates = {"status": "DELIVERED", "dispatch_status": "DELIVERED"}
    order = service.update_order_status(session, order_id, updates)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    service.publish_message("orders", "order.delivered", {"order_id": order_id})
    service.publish_message("notifications", "notify.sms", {"order_id": order_id, "event_type": "ORDER_DELIVERED"})
    return {"status": "DELIVERED", "order_id": order_id}


@router.get("/health")
def health(session: Session = Depends(get_session)):
    return {"status": "healthy", "service": "order"}
