import json
import os
import threading
from twilio.rest import Client as TwilioClient
from shared.amqp import get_connection, setup_exchange

TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.environ.get("TWILIO_FROM_NUMBER", "")
TWILIO_TO = os.environ.get("TWILIO_TO_NUMBER", "")

notification_log = []


def send_sms(to_number, body):
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM]):
        notification_log.append({"to": to_number, "body": body, "status": "MOCK_SENT"})
        return {"status": "MOCK_SENT"}
    try:
        client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(to=to_number, from_=TWILIO_FROM, body=body)
        log_entry = {"to": to_number, "body": body, "sid": message.sid, "status": "SENT"}
        notification_log.append(log_entry)
        return {"sid": message.sid, "status": "queued"}
    except Exception as e:
        notification_log.append({"to": to_number, "body": body, "status": "ERROR", "error": str(e)})
        return {"status": "ERROR", "error": str(e)}


def on_notification(channel, method, properties, body):
    try:
        data = json.loads(body)
        routing_key = method.routing_key
        event_type = "GENERAL"
        message_body = data.get("message", "New notification.")

        if routing_key == "order.confirmed":
            event_type = "ORDER_CONFIRMED"
            message_body = "Order confirmed. Drone assignment pending."
        elif routing_key == "order.failed":
            event_type = "ORDER_CANCELLED"
            message_body = "Order failed."

        sms_body = f"[Medi-Drone | {event_type}] {message_body}"
        send_sms(data.get("phone_number", TWILIO_TO), sms_body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    conn = get_connection()
    channel = conn.channel()
    setup_exchange(channel, "notifications")
    setup_exchange(channel, "orders")

    queue_name = "notification_queue"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange="notifications", queue=queue_name, routing_key="notify.sms")
    channel.queue_bind(exchange="orders", queue=queue_name, routing_key="order.#")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_notification)
    channel.start_consuming()


def run_consumer_thread():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()
    return thread
