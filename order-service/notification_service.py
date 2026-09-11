from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    group_id="notification-service-python",
    auto_offset_reset="earliest",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)

print("Notification Service started...")

for message in consumer:
    event = message.value

    print(
        f"NOTIFICATION: Order #{event['order_id']} "
        f"event = {event['event']}"
    )