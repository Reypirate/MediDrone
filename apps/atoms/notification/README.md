# 🔔 Notification Service

The **Notification Service** is the primary communication bridge between the Medi-Drone platform and its stakeholders (customers, hospital staff, flight operations). It manages asynchronous message delivery across multiple channels.

## 🚀 Features

- **Asynchronous Messaging**: Built on RabbitMQ to handle high-volume event spikes without blocking the core platform.
- **SMS Gateway**: Integration with Twilio for mission-critical order and flight alerts.
- **Event-Driven Lifecycle**: Automatically reacts to system events such as `order.confirmed` and `order.failed`.
- **Audit Logging**: Maintains a rolling historical log of all sent notifications for troubleshooting and analytics.

## 🛠️ Tech Stack

- **FastAPI**: Lightweight API interface for log access.
- **RabbitMQ (AMQP)**: Message broker for reliable delivery.
- **Twilio**: Industry-standard SMS and communication API.
- **UV**: Fast dependency and workspace management.

## 📖 API Documentation

Interactive endpoint documentation and notification history query schemas are served by **Scalar**.

- **Endpoint**: `/scalar`

## 🏁 Getting Started

### Prerequisites

- RabbitMQ instance
- Twilio Account credentials (`SID`, `Auth Token`)

### Local Development

1. **Environment Config**:
   Configure `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_FROM_NUMBER`.
2. **Launch**:
   ```bash
   uv run main.py
   ```

## 🧱 Integration

This service utilizes a specialized background consumer thread to process messages from the `notification_queue`. It binds to both the `notifications` and `orders` exchanges in RabbitMQ.
