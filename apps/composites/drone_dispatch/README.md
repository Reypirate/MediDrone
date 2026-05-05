# 🚁 Drone Dispatch Service

The **Drone Dispatch Service** is a "Composite" service that orchestrates the operational aspects of a drone mission. It acts as the mission controller, coordinating between the order system, fleet management, and spatial engines.

## 🚀 Features

- **Mission Orchestration**: Coordinates the "To Hospital" and "To Target" legs of a medical delivery.
- **Dynamic Routing**: Consolidates data from Route Planning and Weather services to ensure mission safety.
- **Flight Status Hub**: Provides a real-time snapshot of every active delivery mission in the region.
- **Event-Driven Dispatch**: Listens for `order.confirmed` events to automatically spin up a new flight mission.

## 🛠️ Tech Stack

- **FastAPI**: Main API and event-handling layer.
- **SQLModel**: Persistent mission state tracking in PostgreSQL.
- **RabbitMQ**: Reliable event ingestion from the Order system.
- **UV**: Unified workspace dependency management.

## 📖 API Documentation

The full mission orchestration schema and lifecycle endpoints are documented in **Scalar**.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Prerequisites

- PostgreSQL (Mission storage)
- RabbitMQ (Event bus)
- Access to all Atom services (Weather, Route, etc.)

### Local Development

1. **Launch**:
   ```bash
   uv run main.py
   ```

## 🏗️ Technical Workflow

This service implements a "Choreography" pattern:
1. Listens for confirmed orders on the `dispatch_queue`.
2. Resolves drone availability via the **Drone Management** atom.
3. Plans the flight path via **Route Planning**.
4. Creates and tracks the `Mission` entity in the database.
