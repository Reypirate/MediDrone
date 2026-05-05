from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from shared.database import get_session
from . import service

router = APIRouter()

@router.post("/inventory/reserve")
def reserve(data: dict, session: Session = Depends(get_session)):
    result = service.reserve_inventory(session, data)
    if result.get("status") == "FAILED":
        raise HTTPException(status_code=409, detail=result)
    return result

@router.post("/inventory/release")
def release(data: dict, session: Session = Depends(get_session)):
    return service.release_inventory(session, data)

@router.get("/inventory")
def list_inventory(hospital_id: str = None, session: Session = Depends(get_session)):
    return service.get_inventory(session, hospital_id)

@router.get("/inventory/items")
def list_items(session: Session = Depends(get_session)):
    return service.get_distinct_items(session)

@router.get("/inventory/search")
def search(item_id: str, quantity: int = 1, session: Session = Depends(get_session)):
    return service.search_inventory(session, item_id, quantity)

@router.post("/inventory/restock")
def restock(session: Session = Depends(get_session)):
    return service.restock_inventory(session)

@router.get("/health")
def health(session: Session = Depends(get_session)):
    return service.get_health(session)
