import os

from fastapi import FastAPI
from shared.tracking import RequestTrackingMiddleware

app = FastAPI(title="Weather Service")
app.add_middleware(RequestTrackingMiddleware)

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")


@app.get("/weather")
async def get_weather(lat: float, lng: float):
    # Simulated weather for now if no API key
    if not OPENWEATHER_API_KEY:
        return {
            "status": "GOOD",
            "condition": "Clear",
            "temperature": 28.5,
            "wind_speed": 5.2,
            "is_flyable": True,
        }

    # OpenWeather API integration would go here
    return {"status": "GOOD", "is_flyable": True}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "weather"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 4007))
    uvicorn.run(app, host="0.0.0.0", port=port)
