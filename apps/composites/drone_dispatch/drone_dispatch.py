import json
import math
import os
import threading
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from shared.amqp import get_connection, setup_exchange
from shared.database import engine, get_session
from shared.tracking import RequestTrackingMiddleware
from sqlmodel import Field, Session, SQLModel, select

# URLs
ORDER_URL = os.environ.get("ORDER_URL", "http://order:5002")
HOSPITAL_URL = os.environ.get("HOSPITAL_URL", "http://hospital-mock:4003")
GEOLOCATION_URL = os.environ.get("GEOLOCATION_URL", "http://geolocation:4002")
DRONE_MGMT_URL = os.environ.get("DRONE_MGMT_URL", "http://drone-management:4001")
WEATHER_URL = os.environ.get("WEATHER_URL", "http://weather:4007")
ROUTE_URL = os.environ.get("ROUTE_URL", "http://route-planning:4006")

BATTERY_CONSUMPTION_PER_KM = 1.8
LOW_BATTERY_THRESHOLD = 40
DRONE_SPEED_KMH = 36.0
EARTH_RADIUS_KM = 6371.0
POLL_INTERVAL_SECONDS = int(os.environ.get("POLL_INTERVAL", 30))


class Mission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: str = Field(index=True, unique=True)
    drone_id: str
    status: str = "TO_HOSPITAL"
    current_lat: float
    current_lng: float
    target_lat: float
    target_lng: float
    eta_minutes: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


def haversine(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def on_order_confirmed(channel, method, properties, body):
    try:
        data = json.loads(body)
        order_id = data.get("order_id")
        # In a real app, we'd trigger the dispatch orchestration here
        # For this refactor, we'll assume the /dispatch endpoint is called or we trigger it
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


app = FastAPI(title="Drone Dispatch Service")
app.add_middleware(RequestTrackingMiddleware)


@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)
    threading.Thread(target=start_amqp_consumer, daemon=True).start()


@app.post("/dispatch/missions")
def start_mission(data: dict, session: Session = Depends(get_session)):
    order_id = data.get("order_id")
    drone_id = data.get("drone_id")
    # Simulation: start mission logic
    # In reality, this would involve a lot of service coordination
    mission = Mission(
        order_id=order_id,
        drone_id=drone_id,
        current_lat=data.get("start_lat", 1.3521),
        current_lng=data.get("start_lng", 103.8198),
        target_lat=data.get("target_lat", 1.3521),
        target_lng=data.get("target_lng", 103.8198),
        eta_minutes=20.0,
    )
    session.add(mission)
    session.commit()
    return {"status": "SUCCESS", "mission": mission}


@app.get("/dispatch/missions/{order_id}")
def get_mission(order_id: str, session: Session = Depends(get_session)):
    mission = session.exec(select(Mission).where(Mission.order_id == order_id)).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@app.get("/health")
def health():
    return {"status": "healthy", "service": "drone-dispatch"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
