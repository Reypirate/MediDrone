# 📦 Order Service

The **Order Service** is a "Composite" service that serves as the primary entry point for the Medi-Drone platform. It manages the lifecycle of a medical delivery request, from checkout to final fulfillment.

## 🚀 Features

- **Checkout Orchestration**: Validates inventory, geocodes customer addresses, and identifies the optimal fulfillment hospital.
- **Transactional Consistency**: Ensures that inventory is reserved and missions are queued only upon successful order confirmation.
- **Event Emission**: Publishes order status changes (`order.confirmed`, `order.failed`) to the RabbitMQ bus for downstream services.
- **Secure Persistence**: Stores comprehensive order history, item manifests, and customer metadata.

## 🛠️ Tech Stack

- **FastAPI**: Core service framework.
- **SQLModel & PostgreSQL**: Primary data storage and relation management.
- **RabbitMQ**: Outbound event emission.
- **UV**: Modern Python package management.

## 📖 API Documentation

Detailed documentation for the order placement and tracking endpoints is available via **Scalar**.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Prerequisites

- PostgreSQL (Order storage)
- RabbitMQ (Exchange: `orders`)

### Setup

1. **Launch**:
   ```bash
   uv run main.py
   ```

## 🧱 Service Integration

This composite service aggressively integrates with almost every Atom in the ecosystem:
- **Geolocation**: To resolve customer addresses.
- **Inventory**: To verify and decrement stock.
- **Hospital Mock**: To identify delivery source points.
- **Notification**: To alert customers of status changes.
