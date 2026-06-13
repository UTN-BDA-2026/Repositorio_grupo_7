from database.models.Category import Category
from services.base_service import BaseService

class CategoryService(BaseService[Category]):
    pass

category_service = CategoryService(Category)
