import pytest
import uuid
from sqlalchemy import text
from database.db import SessionLocal
from database.models.Category import Category
from services.category_service import category_service


@pytest.fixture
def db_session():
    """
    Entrega una sesión real conectada a PostgreSQL.
    Cierra la sesión al terminar el test.
    """
    session = SessionLocal()
    yield session
    session.close()


@pytest.mark.integration
def test_flujo_completo_postgres(db_session):
    """
    Test de integración que prueba el CRUD completo contra PostgreSQL real.
    Al finalizar, limpia (hard delete) el registro creado para no ensuciar la BD.
    """
    # 1. Crear
    nombre_unico = f"Test_Categoria_{uuid.uuid4().hex[:8]}"
    nueva_cat = category_service.create(db_session, {"name": nombre_unico, "description": "Creada por test de integracion"})
    
    assert nueva_cat.id is not None
    assert nueva_cat.name == nombre_unico
    
    cat_id = nueva_cat.id

    try:
        # 2. Leer
        cat_leida = category_service.get(db_session, cat_id)
        assert cat_leida is not None
        assert cat_leida.name == nombre_unico

        # 3. Actualizar
        cat_actualizada = category_service.update(db_session, cat_leida, {"description": "Actualizada por test"})
        assert cat_actualizada.description == "Actualizada por test"

        # 4. Soft Delete
        cat_borrada = category_service.soft_delete(db_session, cat_id)
        assert cat_borrada.is_active is False
        assert cat_borrada.deleted_at is not None

        # 5. Listar (no deberia traer la borrada, lo validamos filtrando por nombre para asegurar que este test no rompa si hay mas categorias)
        todas = category_service.get_all(db_session)
        nombres_activos = [c.name for c in todas]
        assert nombre_unico not in nombres_activos

    finally:
        # Limpieza: Hard delete usando SQL crudo para borrarla físicamente de la BD de desarrollo
        db_session.execute(text("DELETE FROM categories WHERE id = :cat_id"), {"cat_id": cat_id})
        db_session.commit()
