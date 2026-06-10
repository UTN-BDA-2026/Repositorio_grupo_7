from database.models.BranchProduct import BranchProduct
from services.base_service import BaseService

class BranchProductService(BaseService[BranchProduct]):
    pass

branch_product_service = BranchProductService(BranchProduct)
