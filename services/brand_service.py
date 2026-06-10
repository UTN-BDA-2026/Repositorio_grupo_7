from database.models.Brand import Brand
from services.base_service import BaseService

class BrandService(BaseService[Brand]):
    pass

brand_service = BrandService(Brand)
