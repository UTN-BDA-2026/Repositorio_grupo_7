from database.models.Purchase import Purchase
from services.base_service import BaseService

class PurchaseService(BaseService[Purchase]):
    pass

purchase_service = PurchaseService(Purchase)
