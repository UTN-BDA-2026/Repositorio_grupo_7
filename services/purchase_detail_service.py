from database.models.PurchaseDetail import PurchaseDetail
from services.base_service import BaseService

class PurchaseDetailService(BaseService[PurchaseDetail]):
    pass

purchase_detail_service = PurchaseDetailService(PurchaseDetail)
