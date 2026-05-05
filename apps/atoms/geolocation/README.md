# 📍 Geolocation Service

The **Geolocation Service** is an "Atom" service that provides critical spatial intelligence to the Medi-Drone ecosystem, including coordinate geocoding and geographic boundary validation.

## 🚀 Features

- **Geocoding Engine**: Seamless integration with the Google Maps Places API for high-precision address-to-coordinate conversion.
- **Geofence Validation**: Enforces "Singapore-Only" constraints for drone operations, ensuring compliance with local aviation regulations.
- **Intelligent Caching**: Implements SHA-256 hashed address caching to minimize external API costs and reduce response latency.
- **Resilient Fallbacks**: Provides deterministic fallback coordinates for key hubs (e.g., Changi Airport, Central HQ) during development or API outages.

## 🛠️ Tech Stack

- **FastAPI**: Asynchronous API server for high-concurrency spatial lookups.
- **HTTPX**: Modern, async HTTP client for external API communication.
- **UV**: Project orchestration and dependency management.

## 📖 API Documentation

Detailed documentation for all spatial query endpoints is available via the **Scalar** interface.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Prerequisites

- `GOOGLE_MAPS_API_KEY` (Required for full functionality)

### Local Development

1. **Environmental Setup**:
   ```bash
   export GOOGLE_MAPS_API_KEY="your_api_key_here"
   ```
2. **Execution**:
   ```bash
   uv run main.py
   ```

## 🔐 Security & Validation

All addresses are normalized and hashed before caching to protect potential PII (Personally Identifiable Information) in logs. Geometric validation uses a strict bounding box of Singapore coordinates:
`[Lat: 1.15 - 1.47, Lng: 103.60 - 104.05]`
