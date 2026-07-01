from datetime import datetime, timezone
from nosql.client import get_mongo_db


def log_event(event_type: str, payload: dict) -> None:
    try:
        db = get_mongo_db()
        db.events.insert_one({
            "type": event_type,
            "payload": payload,
            "created_at": datetime.now(timezone.utc)
        })
    except Exception as e:
        print(f"[warn] no se pudo registrar evento NoSQL: {e}")
