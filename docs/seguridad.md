# Seguridad: capas implementadas

## 1. Hashing de contraseñas (bcrypt)

- Ubicación: `services/security.py`
- Algoritmo: bcrypt con salting automático (via `passlib[bcrypt]`)
- Costo: por defecto de bcrypt (12 rondas)
- Se integra en `services/user_service.py`: al crear o actualizar un usuario, la
  contraseña se hashea antes de persistir. Nunca se guarda texto plano.
- Verificación: `verify_password(plain, hashed) -> bool`

## 2. Consultas parametrizadas

- Todas las consultas SQL usan parámetros con nombre (`%(...)s`) en lugar de
  concatenación de strings. Ver `database/transactions.py` para ejemplos.
- El ORM (SQLAlchemy) sanitiza automáticamente los valores en las consultas
  generadas por los servicios (`services/base_service.py`).

## 3. Gestión segura de credenciales

- Las credenciales se leen desde `.env`, nunca desde el código fuente.
- `.env` está incluido en `.gitignore`.
- Variables de entorno requeridas: `DB_USER`, `DB_PASSWORD`, `DB_HOST`,
  `DB_PORT`, `DB_NAME`.

## 4. Seguridad de la conexión (SSL)

- `database/db.py` acepta `DB_SSLMODE` desde `.env`.
- Valores típicos: `prefer` (default), `require`, `verify-ca`, `verify-full`.
- Se pasa como `connect_args` al engine de SQLAlchemy.
