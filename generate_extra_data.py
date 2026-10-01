
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

products = {
    "Laptop": ("Electronics", 55000),
    "Headphones": ("Electronics", 2499),
    "Smartphone": ("Electronics", 25000),
    "Smartwatch": ("Electronics", 5999),
    "T-Shirt": ("Fashion", 799),
    "Jeans": ("Fashion", 1799),
    "Shoes": ("Fashion", 2999),
    "Jacket": ("Fashion", 3499),
    "Coffee Maker": ("Home", 3999),
    "Blender": ("Home", 2499),
    "Backpack": ("Accessories", 1299),
    "Sunglasses": ("Accessories", 999),
}

payment_methods = ["UPI", "Card", "COD", "Net Banking"]
start_time = datetime(2026, 9, 2, 9, 0, 0)

output_file = Path(__file__).parent / "additional_orders.csv"

with output_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "timestamp", "order_id", "product", "category",
        "quantity", "price", "total_amount", "payment_method"
    ])

    for i in range(16, 301):
        product = random.choice(list(products.keys()))
        category, price = products[product]
        quantity = random.choices([1, 2, 3, 4], weights=[55, 27, 13, 5])[0]
        timestamp = start_time + timedelta(
            seconds=(i - 16) * random.randint(30, 180)
        )

        writer.writerow([
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            f"ORD{i:03d}",
            product,
            category,
            quantity,
            price,
            quantity * price,
            random.choice(payment_methods)
        ])

print(f"Generated 285 additional orders: {output_file}")