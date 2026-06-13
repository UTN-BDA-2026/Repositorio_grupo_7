from database.models.SaleDetail import SaleDetail
from services.base_service import BaseService

class SaleDetailService(BaseService[SaleDetail]):
    pass

sale_detail_service = SaleDetailService(SaleDetail)
