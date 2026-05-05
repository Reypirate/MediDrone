from fastapi import APIRouter
from . import service

router = APIRouter()


@router.get("/weather")
async def get_weather(lat: float, lng: float):
    return service.fetch_weather(lat, lng)


@router.get("/health")
def health():
    return {"status": "healthy", "service": "weather"}
