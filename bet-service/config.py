import pymongo
from pymongo.mongo_client import MongoClient
import os

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
DB_NAME = "betting_sports_db"

try:
    mongo_client = MongoClient(MONGO_URI)
    db_handle = mongo_client[DB_NAME]
    
    mongo_client.admin.command('ping') 
    print(f"[{__name__}] MongoDB client initialized successfully.")
except Exception as e:
    print(f"[{__name__}] FATAL ERROR: Could not connect to MongoDB. {e}")