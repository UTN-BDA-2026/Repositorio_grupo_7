# Diccionario de Errores

Este documento recopila problemas frecuentes encontrados durante el desarrollo, ejecución de migraciones y otras tareas dentro de la aplicación, junto con sus respectivas soluciones.

---

## 1. Error de rol inexistente en PostgreSQL (`role "sail" does not exist`)

**Descripción:**
Al ejecutar comandos de migración como `alembic upgrade head`, la base de datos devuelve un error similar a:
```
sqlalchemy.exc.ProgrammingError: (psycopg.errors.UndefinedObject) role "sail" does not exist
```

**Causa:**
El script SQL que se está ejecutando (por ejemplo, `docs/bd_struct.sql`) contiene comandos DDL para reasignar el propietario de las tablas a un usuario de base de datos inexistente. Esto es muy común cuando se utiliza un dump o copia de seguridad exportado desde herramientas de desarrollo como Laravel Sail (cuyo usuario predeterminado suele ser `sail`). Las líneas conflictivas suelen verse así:
```sql
ALTER TABLE public.taxes OWNER TO sail;
```

**Solución:**
Eliminar o reemplazar todas las sentencias `ALTER TABLE ... OWNER TO ...;` de los archivos SQL iniciales. Al omitirlas, las tablas asumen como dueño al usuario que se conecta para ejecutar las consultas, solucionando cualquier discrepancia de permisos en diferentes entornos.

---

## 2. Error de tabla no encontrada en Alembic (`relation "alembic_version" does not exist`)

**Descripción:**
Después de ejecutar correctamente un script SQL a través de Alembic, el proceso falla en su último paso al intentar actualizar la tabla de versiones:
```
sqlalchemy.exc.ProgrammingError: (psycopg.errors.UndefinedTable) relation "alembic_version" does not exist
```

**Causa:**
El script SQL contenía la instrucción:
```sql
SELECT pg_catalog.set_config('search_path', '', false);
```
Esta sentencia vacía el `search_path` de la sesión (es decir, elimina el esquema predeterminado `public`). Puesto que Alembic usa la misma sesión/transacción de la base de datos para intentar acceder e insertar registros en su tabla de control interna (`alembic_version`), se encuentra con que no tiene un esquema donde buscarla (ya que internamente la invoca de forma no calificada, esperando que caiga en el esquema activo predeterminado). 

**Solución:**
Quitar o comentar la línea `SELECT pg_catalog.set_config('search_path', '', false);` del dump o script SQL original. De este modo, PostgreSQL conserva el esquema `public` como entorno activo y permite a Alembic interactuar adecuadamente con sus metadatos sin sufrir pérdidas de referencia.
