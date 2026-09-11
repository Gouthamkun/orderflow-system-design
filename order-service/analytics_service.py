from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "orders",
    bootstrap_servers="localhost:9092",
    group_id="analytics-service-python",
    auto_offset_reset="earliest",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)

print("Analytics Service started...")

order_count = 0

for message in consumer:
    event = message.value

    if event["event"] == "ORDER_CREATED":
        order_count += 1

        print(
            f"ANALYTICS: Order #{event['order_id']} created | "
            f"Total orders = {order_count}"
        )