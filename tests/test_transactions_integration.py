import pytest
import uuid
from database.db import SessionLocal
from database.models import Branch, User, Client, PaymentMethod, CashRegisterSession, Product, BranchProduct, Category, Brand, Tax, Sale
from database.transactions import process_sale_transaction


@pytest.fixture
def db_session():
    """Entrega una sesión de SQLAlchemy para preparar los datos de prueba."""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_data(db_session):
    """
    Crea todos los datos necesarios en la BD para poder hacer una venta sin romper las Foreign Keys.
    Al finalizar el test, borra todo lo que creó.
    """
    # 1. Crear dependencias básicas
    branch = Branch(name="Sucursal Test", address="Calle Falsa 123")
    user = User(name="Cajero Test", email=f"cajero_{uuid.uuid4().hex[:6]}@test.com", password="hash", pos_pin="1234", branch_id=branch.id)
    client = Client(name="Cliente Test", document_type="DNI", document_number=f"DNI_{uuid.uuid4().hex[:6]}", email=f"cliente_{uuid.uuid4().hex[:6]}@test.com")
    payment = PaymentMethod(name=f"Efectivo_{uuid.uuid4().hex[:6]}", surcharge_percentage=0)
    category = Category(name="Cat Test")
    brand = Brand(name="Marca Test", slug=f"marca_{uuid.uuid4().hex[:6]}")
    tax = Tax(name="IVA 21", rate=21.00)
    
    db_session.add_all([branch, user, client, payment, category, brand, tax])
    db_session.flush() # Flush para obtener los IDs sin hacer commit final aún

    # 2. Crear sesión de caja
    session = CashRegisterSession(branch_id=branch.id, user_id=user.id, opening_amount=1000, status='open')
    
    # 3. Crear un producto y asignarle stock inicial de 10 en la sucursal
    product = Product(
        sku=f"SKU_{uuid.uuid4().hex[:6]}", name="Producto Test", barcode=f"BC_{uuid.uuid4().hex[:6]}",
        category_id=category.id, brand_id=brand.id, tax_id=tax.id,
        cost_price=50.0, sale_price=100.0
    )
    db_session.add_all([session, product])
    db_session.flush()

    branch_product = BranchProduct(branch_id=branch.id, product_id=product.id, stock=10.0, alert_stock=2.0)
    db_session.add(branch_product)
    
    # Guardamos todo en la base de datos real
    db_session.commit()

    # Devolvemos un diccionario con los IDs necesarios para armar el JSON de la venta
    data = {
        "branch_id": branch.id,
        "user_id": user.id,
        "client_id": client.id,
        "payment_method_id": payment.id,
        "session_id": session.id,
        "product_id": product.id
    }
    
    yield data

    # LIMPIEZA: Borramos los datos en orden inverso para no romper las FK
    db_session.query(BranchProduct).filter(BranchProduct.product_id == product.id).delete()
    db_session.query(Product).filter(Product.id == product.id).delete()
    db_session.query(CashRegisterSession).filter(CashRegisterSession.id == session.id).delete()
    db_session.query(Tax).filter(Tax.id == tax.id).delete()
    db_session.query(Brand).filter(Brand.id == brand.id).delete()
    db_session.query(Category).filter(Category.id == category.id).delete()
    db_session.query(PaymentMethod).filter(PaymentMethod.id == payment.id).delete()
    db_session.query(Client).filter(Client.id == client.id).delete()
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.query(Branch).filter(Branch.id == branch.id).delete()
    db_session.commit()


@pytest.mark.integration
def test_venta_atomica_exitosa(test_data, db_session):
    """Prueba que una venta normal se procese bien y descuente el stock correctamente."""
    
    sale_data = {
        "branch_id": str(test_data["branch_id"]),
        "user_id": str(test_data["user_id"]),
        "client_id": str(test_data["client_id"]),
        "session_id": str(test_data["session_id"]),
        "payment_method_id": str(test_data["payment_method_id"]),
        "total_amount": 300.00
    }
    
    details_data = [
        {
            "product_id": str(test_data["product_id"]),
            "quantity": 3.0, # Compramos 3 unidades
            "unit_price": 100.00
        }
    ]

    # Ejecutamos la venta
    resultado = process_sale_transaction(sale_data, details_data)
    
    assert resultado["status"] == "success"
    assert resultado["sale_id"] is not None

    # Verificamos que el stock bajó de 10 a 7
    bp = db_session.query(BranchProduct).filter(
        BranchProduct.branch_id == test_data["branch_id"],
        BranchProduct.product_id == test_data["product_id"]
    ).first()
    
    assert bp.stock == 7.0
    
    # Limpieza manual de esta cabecera de venta para que el fixture pueda borrar lo demás
    db_session.query(Sale).filter(Sale.id == resultado["sale_id"]).delete()
    db_session.commit()


@pytest.mark.integration
def test_venta_atomica_falla_por_stock_y_hace_rollback(test_data, db_session):
    """
    Prueba que intentar vender más stock del disponible lanza ValueError 
    y deshace toda la transacción (no descuenta stock ni guarda la venta).
    """
    
    sale_data = {
        "branch_id": str(test_data["branch_id"]),
        "user_id": str(test_data["user_id"]),
        "client_id": str(test_data["client_id"]),
        "session_id": str(test_data["session_id"]),
        "payment_method_id": str(test_data["payment_method_id"]),
        "total_amount": 1500.00
    }
    
    details_data = [
        {
            "product_id": str(test_data["product_id"]),
            "quantity": 15.0, # Intentamos comprar 15 (solo hay 10 en stock)
            "unit_price": 100.00
        }
    ]

    # La función DEBE lanzar un ValueError por falta de stock
    with pytest.raises(ValueError, match="Stock insuficiente"):
        process_sale_transaction(sale_data, details_data)

    # ALERTA DE ROLLBACK: Como falló, el stock debió volver a su estado original (10)
    db_session.expire_all() # Limpiamos caché para obligar a leer de PostgreSQL
    bp = db_session.query(BranchProduct).filter(
        BranchProduct.branch_id == test_data["branch_id"],
        BranchProduct.product_id == test_data["product_id"]
    ).first()
    
    assert bp.stock == 10.0 # El stock está intacto, el rollback funcionó!
