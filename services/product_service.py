from database.models.Product import Product
from services.base_service import BaseService

class ProductService(BaseService[Product]):
    pass

product_service = ProductService(Product)
