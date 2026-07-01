from typing import TypeVar, Generic, Type, Any
from sqlalchemy.orm import Session
from database.db import Base
from datetime import datetime, timezone

ModelType = TypeVar("ModelType", bound=Base)

class BaseService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db:Session, id:Any):
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db:Session, obj_in:dict):
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        try:
            from nosql.events import log_event
            safe_data = {k: v for k, v in obj_in.items() if k != "password"}
            log_event("entity_created", {
                "entity": self.model.__tablename__,
                "id": str(db_obj.id),
                "data": safe_data
            })
        except Exception:
            pass
            
        return db_obj

    def get_all(self, db:Session, skip:int=0, limit:int=100, include_inactive:bool=False, order_by:str=None, order_desc:bool=False):
        query = db.query(self.model)
        if hasattr(self.model, 'is_active') and not include_inactive:
            query = query.filter(self.model.is_active == True)
            
        if order_by and hasattr(self.model, order_by):
            from sqlalchemy import desc
            column = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(column)
                
        return query.offset(skip).limit(limit).all()

    def update(self, db:Session, db_obj:ModelType, obj_in:dict):
        for clave, valor in obj_in.items():
            setattr(db_obj, clave, valor)
            
        if obj_in.get('is_active') is True and hasattr(db_obj, 'deleted_at'):
            db_obj.deleted_at = None
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        try:
            from nosql.events import log_event
            safe_data = {k: v for k, v in obj_in.items() if k != "password"}
            log_event("entity_updated", {
                "entity": self.model.__tablename__,
                "id": str(db_obj.id),
                "changes": safe_data
            })
        except Exception:
            pass
            
        return db_obj

    def soft_delete(self, db:Session, id:Any):
        obj = self.get(db, id)
        if obj:
            if hasattr(obj, 'deleted_at'):
                obj.deleted_at = datetime.now(timezone.utc)
            if hasattr(obj, 'is_active'):
                obj.is_active = False
            db.add(obj)
            db.commit()
            db.refresh(obj)
            
            try:
                from nosql.events import log_event
                log_event("entity_deleted", {
                    "entity": self.model.__tablename__,
                    "id": str(obj.id)
                })
            except Exception:
                pass
                
        return obj

    def count(self, db:Session) -> int:
        return db.query(self.model).count()
