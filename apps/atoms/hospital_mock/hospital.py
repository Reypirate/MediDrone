import os

from fastapi import FastAPI
from shared.tracking import RequestTrackingMiddleware

app = FastAPI(title="Hospital Mock Service")
app.add_middleware(RequestTrackingMiddleware)

HOSPITALS = [
    {"hospital_id": "HOSP-001", "name": "Central General Hospital", "lat": 1.3140, "lng": 103.8442},
    {
        "hospital_id": "HOSP-002",
        "name": "East Coast Medical Center",
        "lat": 1.3413,
        "lng": 103.9533,
    },
    {"hospital_id": "HOSP-003", "name": "West Jurong Hospital", "lat": 1.3329, "lng": 103.7436},
    {"hospital_id": "HOSP-004", "name": "North Woodlands Hospital", "lat": 1.4382, "lng": 103.7891},
    {"hospital_id": "HOSP-005", "name": "Southern Heights Medical", "lat": 1.2819, "lng": 103.8239},
]


@app.get("/hospitals")
def list_hospitals():
    return HOSPITALS


@app.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    for h in HOSPITALS:
        if h["hospital_id"] == hospital_id:
            return h
    return {"error": "Hospital not found"}, 404


@app.get("/health")
def health():
    return {"status": "healthy", "service": "hospital-mock"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 4003))
    uvicorn.run(app, host="0.0.0.0", port=port)
