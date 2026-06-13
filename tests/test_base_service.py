"""
Tests unitarios para BaseService.
Usa SQLite en memoria — no requiere Docker ni PostgreSQL.
"""
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db import Base
from database.models.Category import Category
from services.base_service import BaseService


@pytest.fixture
def db_session():
    """Crea una BD SQLite en memoria, crea las tablas, y entrega una sesión."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def service():
    """Instancia de BaseService usando Category como modelo de prueba."""
    return BaseService(Category)


class TestCreate:
    def test_crear_con_todos_los_campos(self, db_session, service):
        resultado = service.create(db_session, {"name": "Bebidas", "description": "Gaseosas y jugos"})
        assert resultado.name == "Bebidas"
        assert resultado.description == "Gaseosas y jugos"
        assert resultado.id is not None

    def test_crear_con_campos_minimos(self, db_session, service):
        resultado = service.create(db_session, {"name": "Limpieza"})
        assert resultado.name == "Limpieza"
        assert resultado.description is None


class TestGet:
    def test_obtener_por_id_existente(self, db_session, service):
        creado = service.create(db_session, {"name": "Bebidas"})
        encontrado = service.get(db_session, creado.id)
        assert encontrado.id == creado.id
        assert encontrado.name == "Bebidas"

    def test_obtener_id_inexistente_devuelve_none(self, db_session, service):
        resultado = service.get(db_session, uuid.uuid4())
        assert resultado is None


class TestGetAll:
    def test_listar_todos(self, db_session, service):
        service.create(db_session, {"name": "Bebidas"})
        service.create(db_session, {"name": "Limpieza"})
        resultados = service.get_all(db_session)
        assert len(resultados) == 2

    def test_paginacion(self, db_session, service):
        for i in range(5):
            service.create(db_session, {"name": f"Categoría {i}"})
        pagina = service.get_all(db_session, skip=2, limit=2)
        assert len(pagina) == 2

    def test_no_listar_eliminados(self, db_session, service):
        cat = service.create(db_session, {"name": "Temporal"})
        service.soft_delete(db_session, cat.id)
        resultados = service.get_all(db_session)
        assert len(resultados) == 0


class TestUpdate:
    def test_actualizar_campo(self, db_session, service):
        cat = service.create(db_session, {"name": "Bebidasss"})
        actualizado = service.update(db_session, cat, {"name": "Bebidas"})
        assert actualizado.name == "Bebidas"


class TestSoftDelete:
    def test_marca_inactivo_y_deleted_at(self, db_session, service):
        cat = service.create(db_session, {"name": "Temporal"})
        eliminado = service.soft_delete(db_session, cat.id)
        assert eliminado.is_active is False
        assert eliminado.deleted_at is not None

    def test_id_inexistente_devuelve_none(self, db_session, service):
        resultado = service.soft_delete(db_session, uuid.uuid4())
        assert resultado is None
