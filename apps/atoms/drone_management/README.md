# 🛸 Drone Management Service

The **Drone Management Service** is a core "Atom" service responsible for the end-to-end lifecycle management of the Medi-Drone fleet. It handles registration, status tracking, and telemetry ingestion for all active drones.

## 🚀 Features

- **Fleet Lifecycle**: Register new drones, decommission retired units, and manage maintenance schedules.
- **Real-time Status**: Maintain a precise state machine for each drone (e.g., `IDLE`, `EN_ROUTE`, `MAINTENANCE`, `LOW_BATTERY`).
- **Telemetry Processing**: Ingest battery levels, geographic coordinates, and health metrics.
- **Asset Inventory**: Keep detailed records of drone models, max load capacity, and purchase dates.

## 🛠️ Tech Stack

- **FastAPI**: Modern, high-performance web framework for building APIs.
- **SQLModel**: Pydantic-powered ORM for seamless PostgreSQL interaction.
- **UV**: Blazing fast Python package and project manager.
- **PostgreSQL**: Robust relational database for asset persistence.

## 📖 API Documentation

The complete API reference, including request schemas and response models, is served interactively via **Scalar**.

- **Endpoint**: `/scalar`
- **Standard UI**: `/docs` (Swagger) or `/redoc`

## 🏁 Getting Started

### Prerequisites

- Python 3.12+
- `uv` package manager
- Access to the Medi-Drone PostgreSQL instance

### Local Development

1. **Install dependencies**:
   ```bash
   uv sync
   ```
2. **Configure Environment**:
   Ensure `DATABASE_URL` is set in your environment.
3. **Run the service**:
   ```bash
   uv run main.py
   ```

## 🏗️ Architecture

This service follows a modular pattern:
- `models.py`: Data schemas and database entities.
- `service.py`: Business logic and persistence operations.
- `router.py`: API endpoint definitions.
- `main.py`: Application entry point and lifecycle hooks.
