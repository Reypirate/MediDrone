# 🌤️ Weather Service

The **Weather Service** is a safety-critical "Atom" service that monitors atmospheric conditions to determine flight feasibility for the drone fleet.

## 🚀 Features

- **Flyability Status**: Real-time evaluation of weather conditions (wind speed, precipitation, visibility) against drone safety limits.
- **External API Integration**: Capability to ingest data from the OpenWeatherMap API for high-fidelity atmospheric modeling.
- **Deterministic Simulation**: Provides a safe mission-ready status during API outages or development testing.

## 🏛️ Environmental Limits

The service evaluates conditions against established "Go/No-Go" criteria:
- **Wind Speed**: Thresholds for flight stability.
- **Visibility**: Minimum requirements for optical sensors.
- **Precipitation**: Constraints for electronic water resistance.

## 📖 API Documentation

Access the weather query and feasibility check documentation via **Scalar**.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Prerequisites

- `OPENWEATHER_API_KEY` (Optional for simulation, Required for live data)

### Local Development

1. **Execution**:
   ```bash
   uv run main.py
   ```

## 🛠️ Configuration

The service can be customized via environment variables:
- `OPENWEATHER_API_KEY`: External provider key.
- `PORT`: Service port (Default: 4007).
