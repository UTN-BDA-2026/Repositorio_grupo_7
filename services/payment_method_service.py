from database.models.PaymentMethod import PaymentMethod
from services.base_service import BaseService

class PaymentMethodService(BaseService[PaymentMethod]):
    pass

payment_method_service = PaymentMethodService(PaymentMethod)
