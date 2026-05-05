import hashlib
import os
import httpx
from fastapi import HTTPException

GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
SG_BOUNDS = {"lat_min": 1.15, "lat_max": 1.47, "lng_min": 103.60, "lng_max": 104.05}
FALLBACK_COORDINATES = {
    "singapore": {"lat": 1.3521, "lng": 103.8198},
    "changi": {"lat": 1.3644, "lng": 103.9915},
}

geocode_cache = {}


def is_within_singapore(lat, lng):
    return SG_BOUNDS["lat_min"] <= lat <= SG_BOUNDS["lat_max"] and SG_BOUNDS["lng_min"] <= lng <= SG_BOUNDS["lng_max"]


async def perform_geocode(address: str, region: str = "sg"):
    if not address:
        raise HTTPException(status_code=400, detail="address parameter is required")

    addr_hash = hashlib.sha256(address.strip().lower().encode()).hexdigest()
    if addr_hash in geocode_cache:
        return geocode_cache[addr_hash]

    if not GOOGLE_MAPS_API_KEY:
        coords = FALLBACK_COORDINATES.get("singapore")
        resp = {
            "customer_coords": coords,
            "source": "FALLBACK",
            "formatted_address": f"{address} (fallback)",
            "region_valid": True,
        }
        geocode_cache[addr_hash] = resp
        return resp

    async with httpx.AsyncClient() as client:
        params = {"address": address, "key": GOOGLE_MAPS_API_KEY, "region": region}
        res = await client.get(GEOCODE_URL, params=params)
        data = res.json()

        if data.get("status") != "OK":
            raise HTTPException(status_code=502, detail=f"Google API error: {data.get('status')}")

        result = data["results"][0]
        location = result["geometry"]["location"]
        coords = {"lat": location["lat"], "lng": location["lng"]}
        resp = {
            "customer_coords": coords,
            "source": "EXTERNAL_API",
            "formatted_address": result.get("formatted_address"),
            "region_valid": is_within_singapore(coords["lat"], coords["lng"]),
        }
        geocode_cache[addr_hash] = resp
        return resp
