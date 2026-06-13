from database.models.CashRegisterSession import CashRegisterSession
from services.base_service import BaseService

class CashRegisterSessionService(BaseService[CashRegisterSession]):
    pass

cash_register_session_service = CashRegisterSessionService(CashRegisterSession)
