from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from shared.database import get_session
from .models import Drone
from . import service

router = APIRouter()


@router.get("/drones/available")
def get_available(min_battery_pct: int = 30, region: str = "CENTRAL", session: Session = Depends(get_session)):
    return service.get_available_drones(session, min_battery_pct, region)


@router.patch("/drones/{drone_id}/status")
def update_status(drone_id: str, data: dict, session: Session = Depends(get_session)):
    return service.update_drone_status(session, drone_id, data)


@router.get("/drones")
def list_all(session: Session = Depends(get_session)):
    return service.list_all_drones(session)


@router.get("/health")
def health(session: Session = Depends(get_session)):
    try:
        count = session.exec(select(Drone)).all()
        return {"status": "healthy", "service": "drone-management", "drones_count": len(count)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
