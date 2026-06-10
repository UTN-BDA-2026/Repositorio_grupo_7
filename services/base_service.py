from typing import TypeVar, Generic, Type, Any
from sqlalchemy.orm import Session
from database.db import Base
from datetime import datetime

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
        return db_obj

    def get_all(self, db:Session, skip:int=0, limit:int=100):
        return db.query(self.model).offset(skip).limit(limit).all()

    def update(self, db:Session, db_obj:ModelType, obj_in:dict):
        for clave, valor in obj_in.items():
            setattr(db_obj, clave, valor)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db:Session, id:Any):
        obj = self.get(db, id)
        if obj:
            if hasattr(obj, 'deleted_at'):
                obj.deleted_at = datetime.utcnow()
            if hasattr(obj, 'is_active'):
                obj.is_active = False
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj
