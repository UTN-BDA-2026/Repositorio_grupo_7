from typing import Any
from sqlalchemy.orm import Session
from database.models.User import User
from services.base_service import BaseService
from services.security import hash_password

class UserService(BaseService[User]):
    def create(self, db: Session, obj_in: dict) -> User:
        if "password" in obj_in and obj_in["password"]:
            obj_in = {**obj_in, "password": hash_password(obj_in["password"])}
        
        user = super().create(db, obj_in)
        
        from nosql.events import log_event
        log_event("user_created", {
            "target_user_id": str(user.id),
            "target_user_name": user.name,
            "target_user_email": user.email,
        })
        
        return user

    def update(self, db: Session, db_obj: User, obj_in: dict) -> User:
        if "password" in obj_in and obj_in["password"]:
            obj_in = {**obj_in, "password": hash_password(obj_in["password"])}
            
        was_inactive = not getattr(db_obj, 'is_active', True)
        now_active = obj_in.get('is_active', getattr(db_obj, 'is_active', True))
        
        user = super().update(db, db_obj, obj_in)
        
        if was_inactive and now_active:
            from nosql.events import log_event
            log_event("user_restored", {
                "target_user_id": str(user.id),
                "target_user_name": user.name,
                "target_user_email": user.email,
            })
            
        return user

    def soft_delete(self, db: Session, id: Any) -> User:
        user = super().soft_delete(db, id)
        
        from nosql.events import log_event
        log_event("user_deleted", {
            "target_user_id": str(user.id),
            "target_user_name": user.name,
            "target_user_email": user.email,
        })
        
        return user

user_service = UserService(User)
