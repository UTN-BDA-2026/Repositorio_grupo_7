from database.models.Client import Client
from services.base_service import BaseService

class ClientService(BaseService[Client]):
    pass

client_service = ClientService(Client)
