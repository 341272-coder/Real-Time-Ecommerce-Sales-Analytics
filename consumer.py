
import json
from datetime import datetime, timezone

from kafka import KafkaConsumer
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load MongoDB credentials from your existing .env file
load_dotenv(r"D:\SDA-10\.env")
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["ecommerce_analytics"]
orders_collection = db["orders"]

# Kafka setup
consumer = KafkaConsumer(
    "ecommerce_orders",
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    group_id="ecommerce-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("E-commerce Kafka consumer started.")
print("Listening to topic: ecommerce_orders")

count = 0

try:
    for message in consumer:
        order = message.value

        order["ingested_at"] = datetime.now(timezone.utc)

        orders_collection.insert_one(order)

        count += 1
        print(
            f"[{count}] Stored order: {order.get('order_id', 'Unknown')} | "
            f"Product: {order.get('product', 'Unknown')} | "
            f"Amount: {order.get('total_amount', 0)}"
        )

except KeyboardInterrupt:
    print("\nConsumer stopped.")

finally:
    consumer.close()
    client.close()