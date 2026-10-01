
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(r"D:\SDA-10\.env")
client = MongoClient(os.getenv("MONGO_URI"))
db = client["ecommerce_analytics"]
collection = db["orders"]

backup_name = "orders_backup_before_dedup"

try:
    if backup_name in db.list_collection_names():
        raise RuntimeError(f"Backup already exists: {backup_name}")

    total = collection.count_documents({})
    if total != 315:
        raise RuntimeError(f"Expected 315 documents, found {total}")

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
    extra_ids = [
        doc_id
        for group in duplicates
        for doc_id in group["ids"][1:]
    ]

    if len(duplicates) != 15 or len(extra_ids) != 15:
        raise RuntimeError("Duplicate counts differ from the verified preview.")

    # Back up the entire collection before making changes.
    list(collection.aggregate([{"$match": {}}, {"$out": backup_name}]))
    backup_count = db[backup_name].count_documents({})

    if backup_count != total:
        raise RuntimeError("Backup count mismatch; cleanup cancelled.")

    result = collection.delete_many({"_id": {"$in": extra_ids}})
    print(f"Backup created: {backup_name} ({backup_count} documents)")
    print(f"Duplicate documents removed: {result.deleted_count}")
    print(f"Remaining documents: {collection.count_documents({})}")
    print(f"Unique order IDs: {len(collection.distinct('order_id'))}")

except Exception as error:
    print(f"Cleanup stopped: {error}")

finally:
    client.close()