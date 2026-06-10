from database.models.Branch import Branch
from services.base_service import BaseService

class BranchService(BaseService[Branch]):
    pass

branch_service = BranchService(Branch)

