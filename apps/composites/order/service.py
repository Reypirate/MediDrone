import json
import math
import os
import pika
import requests as http_requests
from datetime import datetime
from sqlmodel import Session, select
from shared.amqp import get_connection, setup_exchange
from .models import Order

# Configuration
INVENTORY_URL = os.environ.get("INVENTORY_URL", "http://inventory:4004")
HOSPITAL_URL = os.environ.get("HOSPITAL_URL", "http://hospital-mock:4003")
DISPATCH_URL = os.environ.get("DISPATCH_URL", "http://drone-dispatch:5001")
EARTH_RADIUS_KM = 6371.0


def haversine(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def publish_message(exchange: str, routing_key: str, message: dict):
    try:
        conn = get_connection()
        channel = conn.channel()
        setup_exchange(channel, exchange)
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        conn.close()
    except Exception as e:
        print(f"AMQP Error: {e}")


def find_nearest_hospital(customer_coords, item_id, quantity):
    try:
        resp = http_requests.get(
            f"{INVENTORY_URL}/inventory/search",
            params={"item_id": item_id, "quantity": quantity},
            timeout=10,
        )
        stocked = {h["hospital_id"] for h in resp.json().get("hospitals", [])}
    except Exception as e:
        return None, f"Inventory service unavailable: {e}"

    if not stocked:
        return None, "NO_HOSPITAL_WITH_STOCK"

    try:
        all_hosps = http_requests.get(f"{HOSPITAL_URL}/hospitals", timeout=10).json()
    except Exception as e:
        return None, f"Hospital service unavailable: {e}"

    candidates = []
    for h in all_hosps:
        if h["hospital_id"] in stocked:
            dist = haversine(customer_coords["lat"], customer_coords["lng"], h["lat"], h["lng"])
            candidates.append({**h, "distance_km": dist})

    if not candidates:
        return None, "NO_ACTIVE_HOSPITAL_WITH_STOCK"

    candidates.sort(key=lambda c: c["distance_km"])
    return candidates[0], None


def get_orders(session: Session, status: str = None):
    statement = select(Order)
    if status == "active":
        statement = statement.where(Order.status.in_(["CONFIRMED", "IN_TRANSIT", "DISPATCHED", "IN_FLIGHT"]))
    elif status:
        statement = statement.where(Order.status == status)
    return session.exec(statement).all()


def get_order_by_id(session: Session, order_id: str):
    return session.exec(select(Order).where(Order.order_id == order_id)).first()


def create_order_record(session: Session, order_data: dict):
    new_order = Order(**order_data)
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return new_order


def update_order_status(session: Session, order_id: str, updates: dict):
    order = get_order_by_id(session, order_id)
    if not order:
        return None
    for key, value in updates.items():
        if hasattr(order, key):
            setattr(order, key, value)
    if "dispatch_status" in updates:
        order.status = updates.get("mission_phase", updates["dispatch_status"])
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
