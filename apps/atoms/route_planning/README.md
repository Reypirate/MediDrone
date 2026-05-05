# 🛤️ Route Planning Service

The **Route Planning Service** provides the mathematical engine for optimizing flight paths between hubs and delivery targets. It calculates distances, estimated times of arrival (ETA), and mission waypoints.

## 🚀 Features

- **Geospatial Processing**: Implements the **Haversine formula** to calculate precise "great-circle" distances across the Earth's surface.
- **Waypoint Generation**: Intelligently generates intermediate flight stages to assist drone flight controllers.
- **Temporal Estimation**: Calculates mission duration based on drone-specific performance metrics (e.g., cruising speed).

## 🛠️ Tech Stack

- **FastAPI**: Performance-focused API layer.
- **Math Library**: Native Python precision for nautical and spatial calculations.

## 📖 API Documentation

View the mathematical schemas and routing query parameters through the **Scalar** portal.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Local Development

1. **Execution**:
   ```bash
   uv run main.py
   ```

## 📐 Mathematical Model

The service assumes an Earth Radius ($R$) of **6371 km** and calculates distance ($d$) using:
$$a = \sin^2(\frac{\Delta \phi}{2}) + \cos \phi_1 \cdot \cos \phi_2 \cdot \sin^2(\frac{\Delta \lambda}{2})$$
$$c = 2 \cdot \operatorname{atan2}(\sqrt{a}, \sqrt{1-a})$$
$$d = R \cdot c$$

*Note: For this mock implementation, a constant speed of 0.5 km/min (30 km/h) is used for ETA calculation.*
