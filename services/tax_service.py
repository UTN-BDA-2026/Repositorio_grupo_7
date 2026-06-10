from database.models.Tax import Tax
from services.base_service import BaseService

class TaxService(BaseService[Tax]):
    pass

tax_service = TaxService(Tax)
