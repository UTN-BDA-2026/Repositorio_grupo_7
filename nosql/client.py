import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None

def get_mongo_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(
            os.getenv("MONGO_URI", "mongodb://admin:admin1234@localhost:27018/dba_final_logs?authSource=admin"),
            serverSelectionTimeoutMS=3000
        )
        _db = _client[os.getenv("MONGO_DB", "dba_final_logs")]
    return _db
