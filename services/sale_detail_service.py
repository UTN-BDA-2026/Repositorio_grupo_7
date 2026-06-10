from database.models.SaleDetail import SaleDetail
from service.base_service import BaseService

class SaleDetailService(BaseService[SaleDetail]):
    pass

sale_detail_service = SaleDetailService(SaleDetail)
