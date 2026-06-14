from database.models.Sale import Sale
from services.base_service import BaseService

class SaleService(BaseService[Sale]):
    pass

sale_service = SaleService(Sale)
