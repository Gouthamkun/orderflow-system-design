import json
import threading

from app.redis_client import redis_client
from app.connection_manager import manager


CHANNEL = "order_updates"


def publish_order_update(order_id: int, status: str):

    message = {
        "order_id": order_id,
        "status": status
    }

    redis_client.publish(
        CHANNEL,
        json.dumps(message)
    )


def listen_for_updates():

    pubsub = redis_client.pubsub()
    pubsub.subscribe(CHANNEL)

    print("Redis Pub/Sub listener started...")

    for message in pubsub.listen():

        if message["type"] != "message":
            continue

        data = json.loads(message["data"])

        print("PUB/SUB EVENT:", data)

        order_id = data["order_id"]

        # Run the async broadcast from the background thread
        import asyncio

        asyncio.run(
            manager.broadcast(order_id, data)
        )


def start_listener():

    thread = threading.Thread(
        target=listen_for_updates,
        daemon=True
    )

    thread.start()