from typing import Any
from sqlalchemy.orm import Session
from database.models.User import User
from services.base_service import BaseService
from services.security import hash_password

class UserService(BaseService[User]):
    def create(self, db: Session, obj_in: dict) -> User:
        if "password" in obj_in and obj_in["password"]:
            obj_in = {**obj_in, "password": hash_password(obj_in["password"])}
        return super().create(db, obj_in)

    def update(self, db: Session, db_obj: User, obj_in: dict) -> User:
        if "password" in obj_in and obj_in["password"]:
            obj_in = {**obj_in, "password": hash_password(obj_in["password"])}
        return super().update(db, db_obj, obj_in)

user_service = UserService(User)
