from database.models.InventoryMovement import InventoryMovement
from services.base_service import BaseService

class InventoryMovementService(BaseService[InventoryMovement]):
    pass

inventory_movement_service = InventoryMovementService(InventoryMovement)
