import pytest
from services.security import hash_password, verify_password


class TestHashPassword:
    def test_hash_no_es_texto_plano(self):
        hashed = hash_password("mi_password_segura")
        assert hashed != "mi_password_segura"
        assert hashed.startswith("$2b$")

    def test_hash_distinto_cada_vez(self):
        h1 = hash_password("misma_clave")
        h2 = hash_password("misma_clave")
        assert h1 != h2


class TestVerifyPassword:
    def test_verificar_correcta_devuelve_true(self):
        hashed = hash_password("clave_valida")
        assert verify_password("clave_valida", hashed) is True

    def test_verificar_incorrecta_devuelve_false(self):
        hashed = hash_password("clave_real")
        assert verify_password("clave_equivocada", hashed) is False

    def test_verificar_vacio_devuelve_false(self):
        hashed = hash_password("clave_real")
        assert verify_password("", hashed) is False
