import json
import math
import os
import threading
from sqlmodel import Session, select
from shared.amqp import get_connection, setup_exchange
from .models import Mission

EARTH_RADIUS_KM = 6371.0


def haversine(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def on_order_confirmed(channel, method, properties, body):
    try:
        data = json.loads(body)
        order_id = data.get("order_id")
        print(f" [DISPATCH] Order confirmed: {order_id}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing order: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_amqp_consumer():
    conn = get_connection()
    channel = conn.channel()
    setup_exchange(channel, "orders")
    queue_name = "dispatch_queue"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange="orders", queue=queue_name, routing_key="order.confirmed")
    channel.basic_consume(queue=queue_name, on_message_callback=on_order_confirmed)
    channel.start_consuming()


def run_consumer_thread():
    threading.Thread(target=start_amqp_consumer, daemon=True).start()


def create_mission(session: Session, data: dict):
    mission = Mission(
        order_id=data.get("order_id"),
        drone_id=data.get("drone_id"),
        current_lat=data.get("start_lat", 1.3521),
        current_lng=data.get("start_lng", 103.8198),
        target_lat=data.get("target_lat", 1.3521),
        target_lng=data.get("target_lng", 103.8198),
        eta_minutes=20.0,
    )
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission


def get_mission_by_order(session: Session, order_id: str):
    return session.exec(select(Mission).where(Mission.order_id == order_id)).first()
