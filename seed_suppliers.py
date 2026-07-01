from database.db import get_db
from database.models.Supplier import Supplier

with get_db() as db:
    s1 = Supplier(name="Distribuidora Mayorista S.A.", tax_id="30-12345678-9", email="ventas@mayorista.com", phone="011-555-1234", address="Av. Corrientes 123")
    s2 = Supplier(name="Proveedor Local SRL", tax_id="30-87654321-0", email="contacto@proveedorlocal.com", phone="011-555-9876", address="Calle Falsa 123")
    db.add(s1)
    db.add(s2)
    db.commit()
    print("Proveedores agregados!")
