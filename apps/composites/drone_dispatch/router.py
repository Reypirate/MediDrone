from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from shared.database import get_session
from . import service

router = APIRouter()


@router.post("/dispatch/missions")
def start_mission(data: dict, session: Session = Depends(get_session)):
    return {"status": "SUCCESS", "mission": service.create_mission(session, data)}


@router.get("/dispatch/missions/{order_id}")
def get_mission(order_id: str, session: Session = Depends(get_session)):
    mission = service.get_mission_by_order(session, order_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.get("/health")
def health():
    return {"status": "healthy", "service": "drone-dispatch"}
