from database.models.User import User
from services.base_service import BaseService

class UserService(BaseService[User]):
    pass

user_service = UserService(User)
