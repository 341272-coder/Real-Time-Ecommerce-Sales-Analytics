
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(r"D:\SDA-10\.env")
client = MongoClient(os.getenv("MONGO_URI"))
collection = client["ecommerce_analytics"]["orders"]

pipeline = [
    {"$match": {"order_id": {"$exists": True, "$ne": None}}},
    {"$sort": {"_id": 1}},
    {"$group": {
        "_id": "$order_id",
        "ids": {"$push": "$_id"},
        "count": {"$sum": 1}
    }},
    {"$match": {"count": {"$gt": 1}}}
]

duplicates = list(collection.aggregate(pipeline))
extra_count = sum(item["count"] - 1 for item in duplicates)

print(f"Order IDs with duplicates: {len(duplicates)}")
for item in duplicates:
    print(f"{item['_id']}: {item['count']} copies")

print(f"Extra documents that could be removed: {extra_count}")
print(f"Total documents currently: {collection.count_documents({})}")

client.close()