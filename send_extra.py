
import csv
import json
import time
from pathlib import Path
from kafka import KafkaProducer

csv_file = Path(__file__).parent / "additional_orders.csv"

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

sent = 0

try:
    with csv_file.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["quantity"] = int(row["quantity"])
            row["price"] = float(row["price"])
            row["total_amount"] = float(row["total_amount"])

            producer.send("ecommerce_orders", value=row)
            sent += 1

            print(f"[{sent}/285] Sent order: {row['order_id']}")
            time.sleep(0.2)

    producer.flush()
    print(f"\nSuccessfully sent {sent} additional orders.")

except Exception as e:
    print(f"Error sending orders: {e}")

finally:
    producer.close()