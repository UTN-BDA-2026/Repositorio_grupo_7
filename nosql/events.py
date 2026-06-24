from datetime import datetime, timezone
from nosql.client import db


def log_event(event_type: str, payload: dict) -> None:
    db.events.insert_one({
        "type": event_type,
        "payload": payload,
        "created_at": datetime.now(timezone.utc)
    })
