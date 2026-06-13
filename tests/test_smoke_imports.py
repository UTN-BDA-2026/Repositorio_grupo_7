import pytest

def test_importar_todos_los_servicios():
    from services import(
            branch_product_service,                                                                                                            
            branch_service,                                                                                                                    
            brand_service,                                                                                                                     
            cash_register_session_service,                                                                                                     
            category_service,                                                                                                                  
            client_service,                                                                                                                    
            inventory_movement_service,                                                                                                        
            payment_method_service,                                                                                                            
            product_service,                                                                                                                   
            purchase_detail_service,                                                                                                           
            purchase_service,                                                                                                                  
            sale_detail_service,                                                                                                               
            sale_service,                                                                                                                      
            supplier_service,                                                                                                                  
            tax_service,                                                                                                                       
            user_service,
    )

def test_importar_todos_los_modelos():
    from database.models import(
            Branch, BranchProduct, Brand, CashRegisterSession,
            Category, Client, InventoryMovement, PaymentMethod,
            Product, Purchase, PurchaseDetail, Sale,
            SaleDetail, Supplier, Tax, User,
    )

def test_importar_conexion_db():
    from database.db import Base, SessionLocal, engine
