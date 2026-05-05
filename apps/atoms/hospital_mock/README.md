# 🏥 Hospital Mock Service

The **Hospital Mock Service** serves as a reliable source of truth for healthcare facility metadata within the Medi-Drone ecosystem. It simulates a hospital directory with static geographic and administrative data.

## 🚀 Features

- **Facility Directory**: Provides a comprehensive registry of hospitals across Singapore.
- **Geospatial Metadata**: Includes exact latitude and longitude for each facility to support precise route calculations.
- **Reference Data**: Serves as a stable endpoint for other microservices (Order, Route Planning) to resolve facility identifiers.

## 🏛️ Data Registry

The service currently manages several mock facilities, including:
- **HOSP-001**: Central General Hospital
- **HOSP-002**: East Coast Medical Center
- **HOSP-003**: West Jurong Hospital
- *and more...*

## 📖 API Documentation

Discover and test the facility registry endpoints through the **Scalar** portal.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Local Development

1. **Execution**:
   ```bash
   uv run main.py
   ```

## 🛠️ Architecture

As a lightweight "Atom" service, this module prioritizes:
- **Low Latency**: Static data responses for high-speed resource resolution.
- **Simplicity**: Minimal dependencies, focus on data availability.
