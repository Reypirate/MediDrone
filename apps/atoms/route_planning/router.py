from fastapi import APIRouter
from . import service

router = APIRouter()


@router.get("/route/plan")
def plan_route(start_lat: float, start_lng: float, end_lat: float, end_lng: float):
    return service.calculate_route(start_lat, start_lng, end_lat, end_lng)


@router.get("/health")
def health():
    return {"status": "healthy", "service": "route-planning"}
