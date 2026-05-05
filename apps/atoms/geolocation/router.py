from fastapi import APIRouter
from . import service

router = APIRouter()


@router.get("/maps/api/geocode/json")
async def geocode(address: str, region: str = "sg"):
    return await service.perform_geocode(address, region)


@router.get("/health")
def health():
    return {"status": "healthy", "service": "geolocation", "cache_size": len(service.geocode_cache)}
