import os

# Initialize variables FIRST - must be defined at module level for imports
# This ensures db_handle is always importable, even if MongoDB setup fails
mongo_client = None
db_handle = None
MONGO_URI = None
DB_NAME = "betting_sports_db"

# Try to import pymongo, but don't fail if it's not available
try:
    import pymongo
    from pymongo.mongo_client import MongoClient
    MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
except ImportError as e:
    print(f"[config] Warning: pymongo not available: {e}")
    print(f"[config] MongoDB functionality will be disabled")

def init_mongodb():
    """Initialize MongoDB connection. Returns True if successful."""
    global mongo_client, db_handle, MONGO_URI
    try:
        if not MONGO_URI:
            print(f"[config] Warning: MONGO_CONNECTION_STRING not set, MongoDB disabled")
            return False
        
        # Check if pymongo is available
        try:
            from pymongo.mongo_client import MongoClient
        except ImportError:
            print(f"[config] Warning: pymongo not available")
            return False
        
        print(f"[config] Attempting to connect to MongoDB...")
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db_handle = mongo_client[DB_NAME]
        mongo_client.admin.command('ping')
        print(f"[config] MongoDB client initialized successfully.")
        return True
    except Exception as e:
        print(f"[config] Warning: Could not connect to MongoDB: {e}")
        print(f"[config] App will continue, but database operations may fail")
        # Keep db_handle as None - repository will handle this
        return False

# Try to initialize, but ensure db_handle is always defined (even if None)
if MONGO_URI:
    try:
        init_mongodb()
    except Exception as e:
        print(f"[config] Error during MongoDB initialization: {e}")
        # db_handle remains None, which is acceptable
else:
    print(f"[config] MongoDB URI not configured, db_handle will remain None")