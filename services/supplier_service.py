from database.models.Supplier import Supplier
from services.base_service import BaseService

class SupplierService(BaseService[Supplier]):
    pass

supplier_service = SupplierService(Supplier)
