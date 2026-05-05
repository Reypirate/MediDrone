from fastapi import APIRouter, HTTPException
from . import service

router = APIRouter()


@router.get("/hospitals")
def list_hospitals():
    return service.get_all_hospitals()


@router.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    h = service.find_hospital(hospital_id)
    if not h:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return h


@router.get("/health")
def health():
    return {"status": "healthy", "service": "hospital-mock"}
