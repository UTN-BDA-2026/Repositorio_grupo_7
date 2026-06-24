import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = MongoClient(os.getenv("MONGO_URI", "mongodb://admin:admin1234@localhost:27018/dba_final_logs?authSource=admin"))
db = _client[os.getenv("MONGO_DB", "dba_final_logs")]
