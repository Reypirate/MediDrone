import os

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")


def fetch_weather(lat: float, lng: float):
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
