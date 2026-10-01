




import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(r"D:\SDA-10\.env")

uri = os.getenv("MONGO_URI")

if not uri:
    raise ValueError("MONGO_URI not found in .env")

client = MongoClient(uri, serverSelectionTimeoutMS=15000)

client.admin.command("ping")

print("MongoDB Atlas connection successful!")

db = client["ecommerce_analytics"]
print("Database ready:", db.name)

client.close()