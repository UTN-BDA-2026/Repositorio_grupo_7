# SPEC-03 — Seguridad: endurecimiento

| Campo | Valor |
|---|---|
| **Owner** | Agustín Lara |
| **Rama** | `feat/security-hardening` |
| **Estado** | Borrador |
| **Tema de la consigna** | Seguridad (consultas parametrizadas, variables de entorno, seguridad en la conexión) |
| **Dependencias** | **Ninguna** (solo código de aplicación; no toca el esquema) |
| **Fecha** | 2026-06-24 |

---

## 1. Contexto

El proyecto ya cubre seguridad de base: credenciales en `.env`, consultas
parametrizadas en `database/transactions.py` y el ORM que sanitiza por defecto. Sin
embargo, hay un hueco concreto: **las contraseñas de usuarios** (`users.password`)
se manejan sin hashing en la capa de servicios (`services/user_service.py`), y la
**conexión** no declara modo SSL. Esta spec **refuerza** el tema Seguridad con
mejoras verificables, sin inventar un tema nuevo.

## 2. Objetivo

Endurecer la seguridad de la aplicación: (a) **hashear** contraseñas con un algoritmo
fuerte, (b) reforzar la **seguridad de la conexión** y la gestión de entorno, y
(c) **auditar** que no haya construcción de SQL por concatenación.

## 3. Alcance (in scope)

- Hashing de contraseñas con `passlib[bcrypt]` (o `bcrypt`) en el servicio de usuarios.
- Función de verificación de contraseña (para un eventual login).
- Parámetro `sslmode` configurable en la cadena de conexión (`database/db.py`), por `.env`.
- Auditoría de todo el código: confirmar que no haya f-strings/concatenación en SQL.
- Documentar en `docs/seguridad.md` las 3 capas de seguridad.

## 4. Fuera de alcance (out of scope)

- Sistema completo de login/sesiones en la UI (lo cubre la UI).
- Roles/permisos (RBAC).
- Cambios de esquema (la columna `password` ya es `varchar(255)`, alcanza para el hash).

## 5. Requisitos funcionales

| RF | Descripción |
|---|---|
| RF-1 | Al crear/actualizar un usuario, la contraseña se guarda **hasheada** (bcrypt), nunca en texto plano. |
| RF-2 | Existe `verify_password(plain, hashed) -> bool` para validar credenciales. |
| RF-3 | El hashing está encapsulado en un módulo (`services/security.py`) reutilizable. |
| RF-4 | `database/db.py` acepta `DB_SSLMODE` desde `.env` (p. ej. `prefer`/`require`) y lo agrega a la URL/engine. |
| RF-5 | `.env.example` documenta la nueva variable `DB_SSLMODE`. |
| RF-6 | Auditoría: no existe SQL construido por concatenación de variables (solo parámetros). |

## 6. Diseño técnico

### 6.1 Módulo de seguridad

```python
# services/security.py  (forma de referencia, adaptar)
from passlib.context import CryptContext
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)
```

Integrarlo en `services/user_service.py`: cuando se reciba `password`, guardarlo con
`hash_password(...)`.

### 6.2 Conexión segura

En `database/db.py`, leer `DB_SSLMODE` y pasarlo al engine:

```python
DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")
engine = create_engine(DATABASE_URL, echo=True, connect_args={"sslmode": DB_SSLMODE})
```

### 6.3 Dependencia nueva

Agregar a `requirements.txt`: `passlib[bcrypt]` (fijar versión).

## 7. Entregables

- `services/security.py` (hash/verify).
- `services/user_service.py` integrando el hashing.
- `database/db.py` con `sslmode` configurable.
- `.env.example` actualizado (`DB_SSLMODE`).
- `requirements.txt` actualizado.
- `docs/seguridad.md` documentando las tres capas.
- Test unitario `tests/test_security.py` (hash != plano, verify True/False).

## 8. Criterios de aceptación (Definition of Done)

- [ ] Crear un usuario guarda la contraseña hasheada (verificable: el valor en BD no es el texto plano).
- [ ] `verify_password` devuelve True con la correcta y False con la incorrecta.
- [ ] `DB_SSLMODE` se lee desde `.env` y se aplica al engine.
- [ ] Test `tests/test_security.py` pasa (`pytest`).
- [ ] Auditoría escrita: no hay SQL por concatenación. PR aprobado.

## 9. Plan de verificación

1. `pytest tests/test_security.py` en verde.
2. Crear usuario vía servicio y comprobar en psql que `password` es un hash bcrypt (`$2b$...`).
3. Levantar la app con distintos `DB_SSLMODE` y confirmar que conecta.

## 10. Plan de commits / PR

```
feat: modulo de hashing de contraseñas con bcrypt
feat: integrar hashing en user_service
feat: sslmode configurable en la conexion
test: tests de hashing/verificacion
docs: documentar capas de seguridad
```
PR: **"feat: endurecimiento de seguridad"** → base `main`.

## 11. Notas para la defensa

- Por qué **bcrypt** y no guardar texto plano ni un hash simple (MD5/SHA): salting y costo.
- Qué es una **consulta parametrizada** y cómo previene inyección SQL (mostrar el `%(...)s`
  de `transactions.py`).
- Por qué las credenciales van en `.env` y no en el código (y `.env` en `.gitignore`).
- Qué aporta `sslmode` a la **seguridad de la conexión**.
