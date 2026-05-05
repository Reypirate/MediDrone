from sqlmodel import Session, select
from fastapi import HTTPException
from .models import Drone


def get_available_drones(session: Session, min_battery_pct: int, region: str):
    unavailable_statuses = {
        "IN_FLIGHT",
        "TO_HOSPITAL",
        "TO_CUSTOMER",
        "CHARGING",
        "RETURNING_TO_DEPOT",
        "LOW_BATTERY",
        "FAULTY",
    }

    all_drones = session.exec(select(Drone)).all()
    available = []
    excluded = []

    for d in all_drones:
        if d.status not in unavailable_statuses and d.battery >= min_battery_pct:
            available.append(
                {
                    "drone_id": d.drone_id,
                    "battery_pct": d.battery,
                    "status": d.status,
                    "coords": {"lat": d.lat, "lng": d.lng},
                }
            )
        else:
            reason = (
                d.status
                if d.status in unavailable_statuses
                else ("LOW_BATTERY" if d.battery < min_battery_pct else "UNKNOWN")
            )
            excluded.append(
                {
                    "drone_id": d.drone_id,
                    "battery_pct": d.battery,
                    "status": d.status,
                    "reason": reason,
                }
            )
    return {"region": region, "available_drones": available, "excluded_drones": excluded}


def update_drone_status(session: Session, drone_id: str, data: dict):
    drone = session.get(Drone, drone_id)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")

    for key, value in data.items():
        if hasattr(drone, key):
            setattr(drone, key, value)

    session.add(drone)
    session.commit()
    session.refresh(drone)
    return {"drone_id": drone_id, "status": "UPDATED", "updated_fields": list(data.keys())}


def list_all_drones(session: Session):
    return session.exec(select(Drone)).all()
