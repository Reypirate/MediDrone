import os
import time

import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))


def get_connection():
    max_retries = 12
    delay = 5
    for _attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    heartbeat=300,
                    blocked_connection_timeout=300,
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            time.sleep(delay)
    raise Exception("Could not connect to RabbitMQ")


def setup_exchange(channel, name, type="topic"):
    channel.exchange_declare(exchange=name, exchange_type=type, durable=True)
