# 📦 Inventory Service

The **Inventory Service** manages the SKU-level availability of medical supplies, pharmaceuticals, and emergency equipment across the Medi-Drone fulfillment network.

## 🚀 Features

- **SKU Management**: Add, update, and track medical supplies with specialized metadata (e.g., storage temperature, weight, shelf life).
- **Stock Tracking**: Real-time stock level monitoring with atomic transaction support.
- **Reservation Logic**: Prevent overselling by locking inventory during the order checkout process.
- **Alert System**: Monitor low-stock thresholds to trigger automated replenishment.

## 🛠️ Tech Stack

- **FastAPI**: Robust API layer.
- **SQLModel**: Structured data management with PostgreSQL.
- **UV**: Modern dependency orchestration.

## 📖 API Documentation

The full API schema and interactive testing suite are available via **Scalar**.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Prerequisites

- PostgreSQL database instance
- `uv` installed locally

### Setup

1. **Database initialization**:
   The service automatically handles database migrations and initialization on startup via the `lifespan` hook.
2. **Execution**:
   ```bash
   uv run main.py
   ```

## 🏗️ Technical Details

This service uses **SQLModel** for dual-mode Pydantic/SQLAlchemy interaction, ensuring that all data validation is consistent from the database layer to the API response.
